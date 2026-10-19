"""Streaming XML import from PLEXOS solution ZIPs into SQLite."""

from __future__ import annotations

import sqlite3
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Any

from ..types import XMLRecord
from ..utils import SQLITE_ASCII_CASE_FOLD
from ..xml_records import element_to_record, local_name
from .utils import _quote_ident


class _BOMStripStream:
    """Wrap a binary stream and strip a leading UTF-8 BOM (EF BB BF) if present."""

    _BOM = b"\xef\xbb\xbf"

    def __init__(self, stream: Any) -> None:
        """Wrap *stream*, consuming and discarding a leading UTF-8 BOM if present."""
        self._stream = stream
        # Peek at first 3 bytes; put them back if they are not the BOM.
        head = stream.read(3)
        self._prefix: bytes = b"" if head == self._BOM else head

    def read(self, n: int = -1) -> bytes:
        """Return up to *n* bytes, prepending any saved non-BOM prefix bytes first."""
        if self._prefix:
            if n < 0:
                data = self._prefix + self._stream.read()
                self._prefix = b""
                return data
            chunk = self._prefix[:n]
            self._prefix = self._prefix[len(chunk) :]
            remaining = n - len(chunk)
            return chunk + (self._stream.read(remaining) if remaining > 0 else b"")
        return self._stream.read(n)

    def readable(self) -> bool:  # pragma: no cover
        """Return True; required by the ``io.RawIOBase`` protocol."""
        return True


def _stream_xml_to_sqlite(
    con: sqlite3.Connection,
    stream: Any,
    *,
    batch_size: int = 1_000,
) -> None:
    """Parse XML from a binary stream and insert rows into *con* in batches.

    Uses ``xml.etree.ElementTree.iterparse`` with depth tracking so that only
    *batch_size* row-dicts per table are held in memory at a time.  Each
    completed row element is cleared from the in-memory tree immediately after
    processing, keeping peak memory proportional to the widest batch rather
    than the full XML size.
    """
    if batch_size < 1:
        msg = "batch_size must be positive"
        raise ValueError(msg)
    buffers: dict[str, list[XMLRecord]] = defaultdict(list)
    depth = 0
    root: ET.Element | None = None

    for event, element in ET.iterparse(_BOMStripStream(stream), events=("start", "end")):
        if event == "start":
            depth += 1
            if depth == 1:
                root = element
        else:  # "end"
            if depth == 2 and root is not None:
                # Direct child of root — this is a table-row element.
                tag = local_name(element.tag)
                field_names: dict[str, str] = {}
                aliases: dict[str, str] = {}
                for field in element:
                    name = local_name(field.tag)
                    aliases[name] = field_names.setdefault(name.translate(SQLITE_ASCII_CASE_FOLD), name)
                row = element_to_record(element, rename=aliases)
                buffers[tag].append(row)
                # Detach the processed element from root to free memory.
                element.clear()
                root.clear()
                if len(buffers[tag]) >= batch_size:
                    _create_and_insert_rows(con, tag, buffers.pop(tag))
            depth -= 1

    for tag, rows in buffers.items():
        if rows:
            _create_and_insert_rows(con, tag, rows)


def _create_and_insert_rows(con: sqlite3.Connection, table: str, rows: list[XMLRecord]) -> None:
    """Create a table if needed and insert row dictionaries as TEXT columns."""
    if not rows:
        return

    columns: dict[str, str] = {
        row[1].translate(SQLITE_ASCII_CASE_FOLD): row[1]
        for row in con.execute(f"PRAGMA table_info({_quote_ident(table)})")
    }
    existing = set(columns.values())
    normalized_rows: list[XMLRecord] = []
    for row in rows:
        normalized: XMLRecord = {}
        for name, value in row.items():
            canonical = columns.setdefault(name.translate(SQLITE_ASCII_CASE_FOLD), name)
            normalized[canonical] = value
        normalized_rows.append(normalized)

    all_cols = sorted({col for row in normalized_rows for col in row})
    if not existing:
        col_defs = ", ".join(f"{_quote_ident(col)} TEXT" for col in all_cols)
        con.execute(f"CREATE TABLE {_quote_ident(table)} ({col_defs})")
    else:
        for column in all_cols:
            if column not in existing:
                con.execute(f"ALTER TABLE {_quote_ident(table)} ADD COLUMN {_quote_ident(column)} TEXT")

    placeholders = ", ".join("?" for _ in all_cols)
    col_sql = ", ".join(_quote_ident(col) for col in all_cols)
    values = [tuple(row.get(col) for col in all_cols) for row in normalized_rows]
    con.executemany(
        f"INSERT INTO {_quote_ident(table)} ({col_sql}) VALUES ({placeholders})",
        values,
    )
