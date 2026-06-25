"""PlexosSolution: primary API for PLEXOS solution ZIP import and analysis."""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from pathlib import Path
from types import TracebackType
from typing import Literal
from zipfile import ZipFile

from .archive import _resolve_input_zip_path, _select_xml_entry
from .bin_decoder import _decode_bin_values
from .materialize import _attach_solution_schemas, _build_derived_table_map
from .types import MaterializeResult, SolutionInfo, SQLiteResult, TableInfo
from .xml_parser import _stream_xml_to_sqlite


class PlexosSolution:
    """Fluent interface for importing and querying a PLEXOS solution.

    Two entry points are available:

    * :meth:`from_zip` — bind to a PLEXOS solution ZIP file and use
      :meth:`to_sqlite` to import it.  Both XML metadata and BIN payloads
      are parsed during import.
    * :meth:`from_sqlite` — open an already-imported SQLite database
      directly, without needing the original ZIP file.

    Typical use with a ZIP::

        with PlexosSolution.from_zip("mysolution.zip") as sol:
            result = sol.to_sqlite("output.sqlite")
            sol.materialize_table("Generator")

    Re-opening an existing database (no ZIP needed)::

        sol = PlexosSolution.from_sqlite("output.sqlite")
        show_db_tables(sol)
        sol.materialize_table("Generator")
        sol.close()
    """

    def __init__(self) -> None:
        self._zip_path: Path | None = None
        self._model_name: str | None = None
        self._database_path: Path | None = None
        self._connection: sqlite3.Connection | None = None

    @classmethod
    def from_zip(
        cls,
        path: str | Path,
        *,
        model_name: str | None = None,
    ) -> PlexosSolution:
        """Create a :class:`PlexosSolution` bound to a PLEXOS solution ZIP.

        Parameters
        ----------
        path
            Path to the PLEXOS solution ZIP file.
        model_name
            Optional hint for selecting the correct XML when multiple XML
            files exist inside the archive.
        """
        instance = cls()
        instance._zip_path = _resolve_input_zip_path(path)
        instance._model_name = model_name
        return instance

    @classmethod
    def from_sqlite(
        cls,
        path: str | Path,
    ) -> PlexosSolution:
        """Open an existing PLEXOS solution SQLite database without a source ZIP.

        Useful for reading and querying a database that was previously created
        with :meth:`to_sqlite` or :func:`plexos_to_sqlite`.  No ZIP file is
        required — the XML metadata and BIN payloads are already stored in
        SQLite.

        Parameters
        ----------
        path
            Path to an existing PLEXOS solution SQLite file.

        Raises
        ------
        FileNotFoundError
            If *path* does not exist.
        """
        sqlite_path = Path(path)
        if not sqlite_path.exists():
            raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")
        instance = cls()
        instance._database_path = sqlite_path
        instance._connection = sqlite3.connect(str(sqlite_path))
        _attach_solution_schemas(instance._connection)
        return instance

    def to_sqlite(
        self,
        database: str | Path | None = None,
        *,
        if_exists: Literal["fail", "reuse", "replace"] = "reuse",
        materialize: Literal["none", "all"] | Sequence[str] = "none",
        decode_bin_values: bool = True,
    ) -> SQLiteResult:
        """Import the solution ZIP into a SQLite database.

        Parameters
        ----------
        database
            Filesystem path for the SQLite file.  ``None`` (default) or the
            special string ``':memory:'`` create an in-memory database
            (``if_exists`` is ignored in that case).
        if_exists
            Controls behaviour when *database* already exists on disk:

            ``'fail'``
                Raise :exc:`FileExistsError`.
            ``'reuse'``
                Open the existing file, decode BIN values if missing, and
                attach derived-table schemas.  No re-import is performed.
            ``'replace'``
                Delete the file and create a fresh database.
        decode_bin_values
            If ``True`` (default), decode the BIN payload files from the
            solution ZIP into ``t_data_values``.  Set to ``False`` to skip
            BIN decoding — useful when only the table catalog or XML metadata
            tables are needed, which avoids writing potentially millions of
            rows and is significantly faster for large solutions.
        materialize
            Which derived tables to materialize after import:

            ``'none'``
                Do not materialize any tables (default).
            ``'all'``
                Materialize all available derived tables.
            sequence of strings
                Materialize only the named tables.

        Returns
        -------
        SQLiteResult
            Contains the database path (``None`` for in-memory) and the list
            of table names in the main schema after import.
        """
        if self._zip_path is None:
            raise RuntimeError("No ZIP path configured. Use PlexosSolution.from_zip().")

        in_memory = database is None or database == ":memory:"
        sqlite_path: Path | None = None if in_memory else Path(database)  # type: ignore[arg-type]

        if not in_memory and sqlite_path is not None:
            if sqlite_path.exists():
                if if_exists == "fail":
                    raise FileExistsError(f"Output file already exists: {sqlite_path}")
                if if_exists == "replace":
                    sqlite_path.unlink()
                # if_exists == "reuse": open existing and skip re-import below

        con_str = ":memory:" if in_memory else str(sqlite_path)
        self._connection = sqlite3.connect(con_str)

        _already_imported = (
            not in_memory
            and sqlite_path is not None
            and sqlite_path.exists()
            and if_exists == "reuse"
            and self._connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='solution_metadata' LIMIT 1"
            ).fetchone()
            is not None
        )

        if not _already_imported:
            with ZipFile(self._zip_path, "r") as zf:
                xml_entry = _select_xml_entry(self._zip_path, zf.namelist(), model_name=self._model_name)
                with zf.open(xml_entry, "r") as xml_stream:
                    _stream_xml_to_sqlite(self._connection, xml_stream)
                if decode_bin_values:
                    _decode_bin_values(self._connection, zf)

            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS solution_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            self._connection.executemany(
                "INSERT OR REPLACE INTO solution_metadata(key, value) VALUES (?, ?)",
                [
                    ("source_zip", str(self._zip_path)),
                    ("importer", "plexosdb.PlexosSolution"),
                ],
            )
            self._connection.commit()
        else:
            # Reusing an existing file — decode BIN if not yet done.
            self._ensure_bin_decoded()

        _attach_solution_schemas(self._connection)
        self._apply_materialize(materialize)

        tables = [
            r[0]
            for r in self._connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]
        if not in_memory and sqlite_path is not None:
            self._database_path = sqlite_path
        return SQLiteResult(database=sqlite_path, tables=tables)

    def _apply_materialize(self, materialize: Literal["none", "all"] | Sequence[str]) -> None:
        """Materialize derived tables according to the *materialize* parameter."""
        if materialize == "none":
            return
        import plexosdb.solution_reader as _sr

        con = self.connection  # raises RuntimeError if not connected
        if materialize == "all":
            _sr._materialize_solution_tables(con)
        elif isinstance(materialize, str):
            _sr._materialize_single_solution_table(con, "data", materialize)
            _sr._materialize_single_solution_table(con, "report", materialize)
        else:
            for name in materialize:
                _sr._materialize_single_solution_table(con, "data", name)
                _sr._materialize_single_solution_table(con, "report", name)

    def info(self) -> SolutionInfo:
        """Return metadata about the solution archive.

        Raises
        ------
        RuntimeError
            If no ZIP path has been configured (see :meth:`from_zip`).
        """
        if self._zip_path is None:
            raise RuntimeError("No ZIP path configured. Use PlexosSolution.from_zip().")
        with ZipFile(self._zip_path, "r") as zf:
            xml_entry = _select_xml_entry(self._zip_path, zf.namelist(), model_name=self._model_name)
        return SolutionInfo(
            source=self._zip_path,
            xml_entry=xml_entry,
            model_name=self._model_name,
        )

    def list_tables(
        self,
        *,
        schema: Literal["raw", "processed", "data", "report"] = "report",
    ) -> list[TableInfo]:
        """List tables available under the given *schema*.

        Parameters
        ----------
        schema
            ``'raw'``
                All tables present in the main SQLite schema.
            ``'processed'``
                Core PLEXOS entity tables (class, object, membership, property).
            ``'data'``
                Derived analysis tables (whether materialized or not).
            ``'report'``
                Same as *data* — derived tables exposed under the report schema.
        """
        if schema not in {"raw", "processed", "data", "report"}:
            raise ValueError(f"schema must be 'raw', 'processed', 'data', or 'report'; got {schema!r}")

        con = self.connection  # raises if not open

        if schema == "raw":
            rows = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
            return [TableInfo(name=r[0], schema="raw", table_type="BASE TABLE") for r in rows]

        if schema == "processed":
            _core = frozenset({"t_class", "t_object", "t_membership", "t_property", "t_category"})
            rows = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
            return [
                TableInfo(name=r[0], schema="processed", table_type="BASE TABLE")
                for r in rows
                if r[0] in _core
            ]

        # schema == "data" or "report"
        groups = _build_derived_table_map(con)
        return [
            TableInfo(name=name, schema=schema, table_type="BASE TABLE")
            for (s, name) in sorted(groups)
            if s == "data"
        ]

    def materialize_table(
        self,
        name: str,
        *,
        schema: Literal["data", "report"] = "report",
        if_exists: Literal["fail", "reuse", "replace"] = "reuse",
    ) -> MaterializeResult:
        """Materialize one derived table into the attached *schema*.

        Parameters
        ----------
        name
            Name of the derived table to materialize (e.g. ``'Generator'``).
        schema
            Target schema: ``'data'`` or ``'report'``.
        if_exists
            ``'reuse'`` (default) — return without re-materializing if the
            table already exists.  ``'fail'`` — raise :exc:`FileExistsError`.
            ``'replace'`` — drop the existing table and re-materialize.
        """
        import plexosdb.solution_reader as _sr

        con = self.connection  # raises if not open

        if schema not in {"data", "report"}:
            raise ValueError("schema must be 'data' or 'report'")

        existing = con.execute(
            f"SELECT name FROM {schema}.sqlite_master WHERE type='table' AND name=?",
            (name,),
        ).fetchone()

        if existing is not None:
            if if_exists == "fail":
                raise FileExistsError(f"Table '{name}' already exists in schema '{schema}'")
            if if_exists == "reuse":
                return MaterializeResult(name=name, schema=schema, created=False)
            # replace: drop and fall through to re-create
            con.execute(f"DROP TABLE IF EXISTS {schema}.{name}")
            con.commit()

        created = _sr._materialize_single_solution_table(con, schema, name)
        return MaterializeResult(name=name, schema=schema, created=bool(created))

    @property
    def connection(self) -> sqlite3.Connection:
        """The active SQLite connection.

        Raises
        ------
        RuntimeError
            If :meth:`to_sqlite` has not been called yet.
        """
        if self._connection is None:
            raise RuntimeError("No active connection. Call to_sqlite() before accessing .connection.")
        return self._connection

    def close(self) -> None:
        """Close the active SQLite connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> PlexosSolution:
        """Return *self* for use as a context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the connection on context-manager exit."""
        self.close()

    @property
    def source(self) -> Path | None:
        """Path to the source ZIP file, or ``None`` for :meth:`from_sqlite` instances."""
        return self._zip_path

    @property
    def name(self) -> str:
        """Display name for the solution.

        Returns the stem of the source ZIP when available, then the stem of
        the SQLite database, then ``'unknown'``.
        """
        if self._zip_path is not None:
            return self._zip_path.stem
        if self._database_path is not None:
            return self._database_path.stem
        return "unknown"

    def _ensure_bin_decoded(self) -> None:
        """Decode BIN payloads into ``t_data_values`` if missing or empty."""
        con = self._connection
        if con is None or self._zip_path is None:
            return
        table = con.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='t_data_values' LIMIT 1"
        ).fetchone()
        if table is not None:
            count = con.execute("SELECT COUNT(*) FROM t_data_values").fetchone()[0]
            if count and int(count) > 0:
                return
            con.execute("DROP TABLE IF EXISTS t_data_values")
        with ZipFile(self._zip_path, "r") as zf:
            _decode_bin_values(con, zf)
        con.commit()
