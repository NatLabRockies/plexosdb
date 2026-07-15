"""Shared low-level helpers used across solution_reader submodules."""

from __future__ import annotations


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
