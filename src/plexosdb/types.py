"""Shared XML extraction and SQLite binding contracts."""

from typing import TypeAlias
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidationResult:
    """Result of validating a numeric value against a PLEXOS rule."""

    is_valid: bool
    error_message: str


XMLValue: TypeAlias = str | None
XMLRecord: TypeAlias = dict[str, XMLValue]

SQLiteValue: TypeAlias = str | int | float | bytes | None
SQLiteRecord: TypeAlias = dict[str, SQLiteValue]
