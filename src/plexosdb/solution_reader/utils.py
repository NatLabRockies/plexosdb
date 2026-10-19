"""Shared low-level helpers used across solution_reader submodules."""

from __future__ import annotations

from ..xml_records import local_name as _local_name

__all__ = ["_coerce_value", "_local_name", "_quote_ident"]


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
