"""Data models and public type aliases for DuckDB-backed PLEXOS solutions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal

from .enums import ClassEnum, CollectionEnum

DuckDBSchema = Literal["raw", "processed", "data", "report"]
IfExists = Literal["fail", "reuse", "replace"]
ResultSchema = Literal["data", "report"]


class ResultPhase(StrEnum):
    """PLEXOS solve phases used in result table names."""

    LT = "LT"
    PASA = "PASA"
    MT = "MT"
    ST = "ST"


class ResultPeriod(StrEnum):
    """PLEXOS result periods used in result table names."""

    INTERVAL = "INTERVAL"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"
    HOUR = "HOUR"
    QUARTER = "QUARTER"


class TableType(StrEnum):
    """DuckDB information_schema table types used by solution results."""

    BASE_TABLE = "BASE TABLE"
    VIEW = "VIEW"


@dataclass(frozen=True)
class DuckDBResult:
    """Result returned by :meth:`plexosdb.db_solution.PlexosSolution.to_duckdb`."""

    database: Annotated[
        Path | None,
        "Filesystem path of the DuckDB file, or None for an in-memory database.",
    ] = field(
        metadata={"description": "Filesystem path of the DuckDB file, or None for an in-memory database."}
    )
    tables: Annotated[
        list[str],
        "Names of tables present in the raw DuckDB schema after conversion.",
    ] = field(
        default_factory=list,
        metadata={"description": "Names of tables present in the raw DuckDB schema after conversion."},
    )

    @property
    def is_in_memory(self) -> bool:
        """Return *True* when the database lives in memory only."""
        return self.database is None


@dataclass(frozen=True)
class DuckDBSolutionInfo:
    """Metadata about a DuckDB-backed PLEXOS solution."""

    database: Annotated[
        Path | None,
        "Filesystem path of the DuckDB file, or None for an in-memory database.",
    ] = field(
        metadata={"description": "Filesystem path of the DuckDB file, or None for an in-memory database."}
    )
    source: Annotated[Path | None, "Path to the original PLEXOS solution source, when known."] = field(
        metadata={"description": "Path to the original PLEXOS solution source, when known."}
    )
    model_name: Annotated[str | None, "PLEXOS model name recorded by plexos2duckdb."] = field(
        default=None,
        metadata={"description": "PLEXOS model name recorded by plexos2duckdb."},
    )
    converter_version: Annotated[str | None, "plexos2duckdb converter version."] = field(
        default=None,
        metadata={"description": "plexos2duckdb converter version."},
    )


@dataclass(frozen=True)
class TableInfo:
    """Metadata about one table or view in a DuckDB solution schema."""

    name: Annotated[str, "DuckDB table or view name."] = field(
        metadata={"description": "DuckDB table or view name."}
    )
    schema: Annotated[str, "DuckDB schema containing the table or view."] = field(
        metadata={"description": "DuckDB schema containing the table or view."}
    )
    table_type: Annotated[str, "DuckDB information_schema table type."] = field(
        metadata={"description": "DuckDB information_schema table type."}
    )


@dataclass(frozen=True)
class ResultTable:
    """Metadata for one PLEXOS solution result table or view."""

    name: Annotated[str, "DuckDB table or view name."] = field(
        metadata={"description": "DuckDB table or view name."}
    )
    schema: Annotated[ResultSchema, "DuckDB schema containing the result."] = field(
        metadata={"description": "DuckDB schema containing the result."}
    )
    phase: Annotated[ResultPhase, "PLEXOS solve phase."] = field(
        metadata={"description": "PLEXOS solve phase."}
    )
    period: Annotated[ResultPeriod, "PLEXOS result period."] = field(
        metadata={"description": "PLEXOS result period."}
    )
    class_enum: Annotated[ClassEnum | None, "Object class associated with the result collection."] = field(
        metadata={"description": "Object class associated with the result collection."}
    )
    collection: Annotated[CollectionEnum, "PLEXOS collection represented by the result."] = field(
        metadata={"description": "PLEXOS collection represented by the result."}
    )
    property_name: Annotated[str, "PLEXOS property represented by the result."] = field(
        metadata={"description": "PLEXOS property represented by the result."}
    )
    table_type: Annotated[TableType, "DuckDB information_schema table type."] = field(
        metadata={"description": "DuckDB information_schema table type."}
    )
    value_column: Annotated[str, "Column containing the result values."] = field(
        metadata={"description": "Column containing the result values."}
    )
