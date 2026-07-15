"""Result and metadata types for the PlexosSolution API."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SolutionInfo:
    """Metadata about a PLEXOS solution archive."""

    source: Path
    xml_entry: str
    model_name: str | None = None


@dataclass
class SQLiteResult:
    """Result returned by :meth:`PlexosSolution.to_sqlite`."""

    database: Path | None
    """Filesystem path of the SQLite file, or *None* for an in-memory database."""

    tables: list[str] = field(default_factory=list)
    """Names of all tables present in the main SQLite schema after import."""

    @property
    def is_in_memory(self) -> bool:
        """Return *True* when the database lives in memory only."""
        return self.database is None


@dataclass(frozen=True)
class TableInfo:
    """Metadata about one table or view in a solution schema."""

    name: str
    schema: str
    table_type: str
    """``'BASE TABLE'`` or ``'VIEW'``."""


@dataclass(frozen=True)
class MaterializeResult:
    """Result returned by :meth:`PlexosSolution.materialize_table`."""

    name: str
    schema: str
    created: bool
    """*True* when the table was newly created; *False* when it was skipped
    because it already existed and ``if_exists='reuse'`` was in effect."""
