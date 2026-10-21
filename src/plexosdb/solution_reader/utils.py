"""Shared low-level helpers used across solution_reader submodules."""

from __future__ import annotations

import sqlite3

from ..types import SQLiteValue

# Unicode whitespace recognized by str.strip(), including non-XML whitespace.
STRIP_CHARACTERS = (
    "\t\n\v\f\r\x1c\x1d\x1e\x1f \x85\xa0\u1680"
    "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000"
)


def integer_reference_sql(column: str, /) -> str:
    """Build an integer reference using the same conversion as BIN metadata."""
    identifier = ".".join(_quote_ident(part) for part in column.split("."))
    return f"CAST(plexos_integer_reference({identifier}) AS TEXT)"


def _integer_reference(value: SQLiteValue, /) -> int | str | None:
    """Return an exact canonical identity within SQLite's integer-size limit."""
    integer = parse_optional_integer(value)
    if integer is None or -(2**63) <= integer < 2**63:
        return integer
    return str(integer)


def register_integer_references(con: sqlite3.Connection, /) -> None:
    """Install the deterministic conversion used by materialization and its indexes."""
    if any(
        row[0] == "plexos_integer_reference" and row[4] == 1 for row in con.execute("PRAGMA function_list")
    ):
        return
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


def _local_name(tag: str) -> str:
    """Return the local XML tag name without namespace prefix."""
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


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
