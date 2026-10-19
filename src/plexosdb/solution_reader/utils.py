"""Shared low-level helpers used across solution_reader submodules."""

from __future__ import annotations

import sqlite3

from ..types import SQLiteValue
from ..xml_records import local_name as _local_name

__all__ = ["_coerce_value", "_local_name", "_quote_ident", "parse_optional_integer"]

# Unicode whitespace recognized by str.strip(), including non-XML whitespace.
STRIP_CHARACTERS = (
    "\t\n\v\f\r\x1c\x1d\x1e\x1f \x85\xa0\u1680"
    "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000"
)


def integer_reference_sql(column: str, /) -> str:
    """Build an integer reference using the same conversion as BIN metadata."""
    identifier = ".".join(_quote_ident(part) for part in column.split("."))
    return f"CAST(plexos_integer_reference({identifier}) AS INTEGER)"


def _integer_reference(value: SQLiteValue, /) -> str | None:
    """Return canonical integer text without SQLite's callback integer-size limit."""
    integer = parse_optional_integer(value)
    return str(integer) if integer is not None else None


def register_integer_references(con: sqlite3.Connection, /) -> None:
    """Install the deterministic conversion used by materialization and its indexes."""
    con.create_function("plexos_integer_reference", 1, _integer_reference, deterministic=True)


def parse_optional_integer(value: SQLiteValue, /) -> int | None:
    """Parse optional numeric metadata, treating NULL and blank text as absent."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    return int(value)


def _quote_ident(identifier: str) -> str:
    """Return a safely quoted SQLite identifier."""
    escaped = identifier.replace('"', '""')
    return f'"{escaped}"'


def _coerce_value(value: str | None) -> int | float | str | None:
    """Coerce XML text values to int, float, or normalized string/None."""
    if value is None:
        return None
    text = value.strip()
    if text == "":
        return None
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text
