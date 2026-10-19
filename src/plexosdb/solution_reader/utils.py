"""Shared low-level helpers used across solution_reader submodules."""

from __future__ import annotations

from ..types import SQLiteValue
from ..xml_records import local_name as _local_name

__all__ = ["_coerce_value", "_local_name", "_quote_ident", "parse_optional_integer"]

# Unicode whitespace recognized by str.strip(), including non-XML whitespace.
STRIP_CHARACTERS = (
    "\t\n\v\f\r\x1c\x1d\x1e\x1f \x85\xa0\u1680"
    "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000"
)


def integer_reference_sql(column: str, /) -> str:
    """Build a native SQLite integer reference, preserving NULL and blank IDs."""
    identifier = ".".join(_quote_ident(part) for part in column.split("."))
    text = (
        f"CASE WHEN {identifier} GLOB '[0-9]*' THEN {identifier} "
        f"ELSE TRIM({identifier}, '{STRIP_CHARACTERS}') END"
    )
    # The outer CAST retains integer affinity for expression-index lookups.
    return f"CAST(NULLIF({text}, '') AS INTEGER)"


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
