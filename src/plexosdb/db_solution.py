"""Wrapper of PLEXOS2duckdb."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from types import TracebackType
from typing import Any

import duckdb

from .db_solution_helpers import (
    get_solution_result_table,
    list_solution_objects_by_class,
    list_solution_result_tables,
    open_solution_connection,
    query_dict_rows,
    query_rows,
    read_solution_result,
    solution_metadata_source,
    solution_metadata_value,
    solution_table_names,
    sql_relation,
    table_relation,
)
from .db_solution_models import (
    DuckDBResult,
    DuckDBSchema,
    DuckDBSolutionInfo,
    IfExists,
    ResultSchema,
    ResultTable,
    TableInfo,
)
from .enums import ClassEnum, CollectionEnum, PeriodEnum, PhaseEnum

_FACTORY_TOKEN = object()


class PlexosSolution:
    """PLEXOS solution wrapper backed by ``plexos2duckdb``.

    Passing ``database`` to :meth:`to_duckdb` creates or reuses a file-backed
    DuckDB database, which is the fastest path for large solutions.  Omitting
    ``database`` keeps the result in memory by converting through a temporary
    DuckDB file and copying it into an in-memory DuckDB connection.
    """

    _zip_path: Path | None
    _model_name: str | None
    _database_path: Path | None
    _connection: duckdb.DuckDBPyConnection | None

    def __init__(
        self,
        source_path: str | Path | None = None,
        *,
        model_name: str | None = None,
        _factory_token: object | None = None,
    ) -> None:
        """Prevent direct construction; use a named factory instead."""
        if _factory_token is not _FACTORY_TOKEN:
            raise TypeError("Use PlexosSolution.from_zip(...) to create a solution.")
        if source_path is None:
            raise TypeError("source_path is required for internal PlexosSolution construction.")
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"PLEXOS solution path not found: {source}")
        self._zip_path = source
        self._model_name = model_name
        self._database_path = None
        self._connection = None

    @classmethod
    def from_zip(
        cls,
        path: str | Path,
        *,
        model_name: str | None = None,
    ) -> PlexosSolution:
        """Create a solution wrapper bound to a PLEXOS solution path."""
        return cls(path, model_name=model_name, _factory_token=_FACTORY_TOKEN)

    def to_duckdb(
        self,
        database: str | Path | None = None,
        *,
        if_exists: IfExists = "reuse",
        n_threads: int | None = None,
        table_name_pattern: str | None = None,
        in_memory: bool | None = None,
    ) -> DuckDBResult:
        """Convert the solution with ``plexos2duckdb`` and open a DuckDB connection.

        Parameters
        ----------
        database
            Output DuckDB path. When omitted, the result is in memory unless
            ``in_memory=False`` is provided.
        if_exists
            File-backed overwrite policy: ``'fail'``, ``'reuse'``, or ``'replace'``.
            Ignored for in-memory conversion because the intermediate database is
            temporary.
        n_threads
            Optional thread count passed to ``plexos2duckdb`` for time-series table writes.
        table_name_pattern
            Optional regex passed to ``plexos2duckdb`` to restrict generated data tables.
        in_memory
            ``True`` forces an in-memory final connection, ``False`` forces a
            file-backed database, and ``None`` uses in memory when *database* is omitted.
        """
        if self._zip_path is None:
            raise RuntimeError("No ZIP path configured. Use PlexosSolution.from_zip().")
        if if_exists not in {"fail", "reuse", "replace"}:
            raise ValueError("if_exists must be 'fail', 'reuse', or 'replace'")

        use_memory = database is None if in_memory is None else in_memory
        self.close()
        self._connection, self._database_path = open_solution_connection(
            self._zip_path,
            database,
            if_exists=if_exists,
            n_threads=n_threads,
            table_name_pattern=table_name_pattern,
            in_memory=use_memory,
        )
        return DuckDBResult(
            database=self._database_path,
            tables=solution_table_names(self.connection, schema="raw"),
        )

    def info(self) -> DuckDBSolutionInfo:
        """Return metadata about the configured or converted DuckDB solution."""
        return DuckDBSolutionInfo(
            database=self._database_path,
            source=self._zip_path or solution_metadata_source(self._connection),
            model_name=solution_metadata_value(self._connection, "model_name") or self._model_name,
            converter_version=solution_metadata_value(self._connection, "plexos2duckdb_version"),
        )

    def list_tables(
        self,
        *,
        schema: DuckDBSchema = "report",
    ) -> list[TableInfo]:
        """List tables or views in one DuckDB solution schema."""
        rows = self.connection.execute(
            """
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_catalog = current_database()
              AND table_schema = ?
            ORDER BY table_name
            """,
            (schema,),
        ).fetchall()
        return [
            TableInfo(name=str(name), schema=schema, table_type=str(table_type)) for name, table_type in rows
        ]

    def sql(self, query_string: str) -> duckdb.DuckDBPyRelation:
        """Build a lazy DuckDB relation from a SQL query."""
        return sql_relation(self.connection, query_string)

    def query(
        self,
        query_string: str,
        params: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> list[Any]:
        """Execute a read-only query and return all rows."""
        return query_rows(self.connection, query_string, params=params)

    def query_dicts(
        self,
        query_string: str,
        params: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a read-only query and return rows as dictionaries."""
        return query_dict_rows(self.connection, query_string, params=params)

    def table(
        self,
        table: str | ResultTable,
        *,
        schema: DuckDBSchema = "report",
    ) -> duckdb.DuckDBPyRelation:
        """Build a lazy DuckDB relation for a solution table or view."""
        return table_relation(self.connection, table, schema=schema)

    def list_objects_by_class(
        self,
        class_enum: ClassEnum | str,
        /,
        *,
        category: str | None = None,
    ) -> list[str]:
        """Return solution object names for a PLEXOS class."""
        return list_solution_objects_by_class(self.connection, class_enum, category=category)

    def list_result_tables(
        self,
        *,
        schema: ResultSchema = "report",
        phase: PhaseEnum | str | None = None,
        period: PeriodEnum | str | None = None,
        class_enum: ClassEnum | str | None = None,
        collection: CollectionEnum | str | None = None,
        property_name: str | None = None,
    ) -> list[ResultTable]:
        """List result tables using PLEXOS class, collection, and property filters."""
        return list_solution_result_tables(
            self.connection,
            schema=schema,
            phase=phase,
            period=period,
            class_enum=class_enum,
            collection=collection,
            property_name=property_name,
        )

    def result_table(
        self,
        *,
        schema: ResultSchema = "report",
        phase: PhaseEnum | str = PhaseEnum.ST,
        period: PeriodEnum | str = PeriodEnum.INTERVAL,
        class_enum: ClassEnum | str | None = None,
        collection: CollectionEnum | str | None = None,
        property_name: str,
    ) -> ResultTable:
        """Return one result table matching PLEXOS dimensions."""
        return get_solution_result_table(
            self.connection,
            schema=schema,
            phase=phase,
            period=period,
            class_enum=class_enum,
            collection=collection,
            property_name=property_name,
        )

    def get_result(
        self,
        table_name: ResultTable | str,
        /,
        *,
        object_names: str | Iterable[str] | None = None,
        category: str | None = None,
        sample_names: str | Iterable[str] | None = "Mean",
        bands: int | Iterable[int] | None = None,
        start: str | None = None,
        end: str | None = None,
        columns: Sequence[str] | None = None,
    ) -> duckdb.DuckDBPyRelation:
        """Build a lazy relation for filtered rows from a result table."""
        return read_solution_result(
            self.connection,
            table_name,
            object_names=object_names,
            category=category,
            sample_names=sample_names,
            bands=bands,
            start=start,
            end=end,
            columns=columns,
        )

    @property
    def connection(self) -> duckdb.DuckDBPyConnection:
        """The active DuckDB connection."""
        if self._connection is None:
            raise RuntimeError("No active connection. Call to_duckdb() before accessing .connection.")
        return self._connection

    def close(self) -> None:
        """Close the active DuckDB connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> PlexosSolution:
        """Return ``self`` for context-manager use."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the active DuckDB connection on context exit."""
        self.close()
