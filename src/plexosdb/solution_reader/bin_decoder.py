"""Binary value payload decoding for PLEXOS solution t_data_*.BIN files."""

from __future__ import annotations

import sqlite3
import struct
from collections import defaultdict
from typing import Any
from zipfile import ZipFile


def _read_all_bin_entries(zf: ZipFile) -> dict[int, bytes]:
    """Read all binary data entries keyed by period type id."""
    period_bytes: dict[int, bytes] = {}
    for name in zf.namelist():
        lower_name = name.lower()
        if not lower_name.startswith("t_data_") or not lower_name.endswith(".bin"):
            continue
        suffix = lower_name[len("t_data_") : -len(".bin")]
        try:
            period_type_id = int(suffix)
        except ValueError:
            continue
        period_bytes[period_type_id] = zf.read(name)
    return period_bytes


def _bin_entry_name_map(zf: ZipFile) -> dict[int, str]:
    """Map period_type_id -> ZIP entry name for t_data_<id>.BIN files."""
    names: dict[int, str] = {}
    for name in zf.namelist():
        lower_name = name.lower()
        if not lower_name.startswith("t_data_") or not lower_name.endswith(".bin"):
            continue
        suffix = lower_name[len("t_data_") : -len(".bin")]
        try:
            period_type_id = int(suffix)
        except ValueError:
            continue
        names[period_type_id] = name
    return names


def _skip_bytes(stream: Any, nbytes: int) -> bool:
    """Advance a stream by nbytes, returning False if EOF is reached early."""
    remaining = nbytes
    chunk_size = 1024 * 1024
    while remaining > 0:
        chunk = stream.read(min(chunk_size, remaining))
        if not chunk:
            return False
        remaining -= len(chunk)
    return True


def _group_key_rows_by_period(
    key_rows: list[tuple[Any, Any, Any, Any, Any]],
    period_entries: dict[int, str],
) -> dict[int, list[tuple[int, int, int, int]]]:
    """Group decoded key-index rows by period type for BIN decoding."""
    rows_by_period: dict[int, list[tuple[int, int, int, int]]] = defaultdict(list)
    for key_id, period_type_id, length, position, period_offset in key_rows:
        try:
            period_type = int(period_type_id)
            num_values = int(length)
            byte_pos = int(position)
            offset = int(period_offset)
            key_id_int = int(key_id)
        except (TypeError, ValueError):
            continue

        if period_type not in period_entries or num_values <= 0:
            continue

        rows_by_period[period_type].append((key_id_int, num_values, byte_pos, offset))

    return rows_by_period


def _decode_period_rows(
    zf: ZipFile,
    entry_name: str,
    period_type: int,
    rows: list[tuple[int, int, int, int]],
) -> Any:
    """Yield decoded t_data_values rows for one period BIN entry."""
    # Read keys in byte-order to minimize stream movement and memory overhead.
    sorted_rows = sorted(rows, key=lambda x: x[2])
    with zf.open(entry_name, "r") as stream:
        current_pos = 0
        for key_id, num_values, byte_pos, offset in sorted_rows:
            if byte_pos < current_pos:
                # Defensive fallback for unexpected non-monotonic positions.
                try:
                    stream.seek(byte_pos)
                    current_pos = byte_pos
                except Exception:
                    continue

            if byte_pos > current_pos:
                ok = _skip_bytes(stream, byte_pos - current_pos)
                if not ok:
                    continue
                current_pos = byte_pos

            byte_len = num_values * 8
            chunk = stream.read(byte_len)
            if len(chunk) != byte_len:
                continue
            current_pos += byte_len

            values = struct.unpack(f"<{num_values}d", chunk)
            for idx, value in enumerate(values):
                block_id = offset + idx + 1
                yield (key_id, period_type, block_id, float(value))


def _decode_bin_values(con: sqlite3.Connection, zf: ZipFile) -> None:
    """Decode BIN payloads into t_data_values when key index metadata exists."""
    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "t_key_index" not in table_names:
        return

    key_rows = con.execute(
        "SELECT key_id, period_type_id, length, position, COALESCE(period_offset, 0) FROM t_key_index"
    ).fetchall()
    if not key_rows:
        return

    period_entries = _bin_entry_name_map(zf)
    if not period_entries:
        return

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS t_data_values (
            key_id INTEGER NOT NULL,
            period_type_id INTEGER NOT NULL,
            block_id INTEGER NOT NULL,
            value REAL NOT NULL
        )
        """
    )

    rows_by_period = _group_key_rows_by_period(key_rows, period_entries)

    if not rows_by_period:
        return

    insert_sql = "INSERT INTO t_data_values(key_id, period_type_id, block_id, value) VALUES (?, ?, ?, ?)"
    batch: list[tuple[int, int, int, float]] = []
    batch_size = 100_000

    for period_type, rows in rows_by_period.items():
        entry_name = period_entries.get(period_type)
        if entry_name is None:
            continue

        for row in _decode_period_rows(zf, entry_name, period_type, rows):
            batch.append(row)
            if len(batch) >= batch_size:
                con.executemany(insert_sql, batch)
                batch.clear()

    if batch:
        con.executemany(insert_sql, batch)
