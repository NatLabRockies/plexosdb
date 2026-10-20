"""Shared XML extraction and SQLite binding contracts."""

from typing import TypeAlias

XMLValue: TypeAlias = str | None
XMLRecord: TypeAlias = dict[str, XMLValue]

SQLiteValue: TypeAlias = str | int | float | bytes | None
SQLiteRecord: TypeAlias = dict[str, SQLiteValue]
