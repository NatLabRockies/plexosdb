"""Public API: plexos_to_sqlite function and PLEXOS2SQLite class."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from zipfile import ZipFile

from ._bin_decode import _decode_bin_values
from ._materialize import (
    _attach_solution_schemas,
    _build_derived_table_map,
    _materialize_solution_tables,
)
from ._xml_import import _stream_xml_to_sqlite
from ._zip import _resolve_input_zip_path, _select_xml_entry


def plexos_to_sqlite(
    zip_path: str | Path,
    sqlite_path: str | Path | None = None,
    *,
    model_name: str | None = None,
    decode_bin_values: bool = True,
) -> sqlite3.Connection:
    """Import a PLEXOS solution ZIP into SQLite using pure Python.

    Parameters
    ----------
    zip_path
        Path to the PLEXOS solution ZIP file.
    sqlite_path
        Optional SQLite output file path. If None, an in-memory database is used.
    model_name
        Optional model-name hint used to pick the XML when multiple XML files exist.
    decode_bin_values
        If True, decode BIN value payloads into ``t_data_values`` during import.
        Set False to only import XML tables and defer BIN decoding.

    Returns
    -------
    sqlite3.Connection
        SQLite connection populated from ZIP XML tables and decoded BIN values.
    """
    zip_path = _resolve_input_zip_path(zip_path)

    con = sqlite3.connect(str(sqlite_path) if sqlite_path else ":memory:")

    with ZipFile(zip_path, "r") as zf:
        xml_entry = _select_xml_entry(zip_path, zf.namelist(), model_name=model_name)
        with zf.open(xml_entry, "r") as xml_stream:
            _stream_xml_to_sqlite(con, xml_stream)

        if decode_bin_values:
            _decode_bin_values(con, zf)

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS solution_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    con.executemany(
        "INSERT OR REPLACE INTO solution_metadata(key, value) VALUES (?, ?)",
        [
            ("source_zip", str(zip_path)),
            ("importer", "plexosdb.plexos_to_sqlite"),
        ],
    )
    con.commit()
    return con


class PLEXOS2SQLite:
    """Class interface for converting PLEXOS solution ZIP files to SQLite."""

    def __init__(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        *,
        force: bool = False,
        model_name: str | None = None,
        materialize_on_enter: bool = True,
        decode_on_convert: bool | None = None,
    ) -> None:
        """Initialize converter configuration and output path behavior."""
        self.input_path = _resolve_input_zip_path(input_path)
        self.output_path = (
            Path(output_path) if output_path is not None else self.input_path.with_suffix(".sqlite")
        )
        self.force = force
        self.model_name = model_name
        self.materialize_on_enter = materialize_on_enter
        self.decode_on_convert = materialize_on_enter if decode_on_convert is None else decode_on_convert
        self.connection: sqlite3.Connection | None = None

    def convert(self) -> str:
        """Convert the input ZIP file to a SQLite database file and return its path."""
        if self.output_path.exists() and not self.force:
            raise FileExistsError(
                f"Output file already exists: {self.output_path}. Set force=True to overwrite it."
            )

        if self.output_path.exists() and self.force:
            self.output_path.unlink()

        con = plexos_to_sqlite(
            self.input_path,
            sqlite_path=self.output_path,
            model_name=self.model_name,
            decode_bin_values=self.decode_on_convert,
        )
        con.close()
        return str(self.output_path)

    def _ensure_data_values_decoded(self) -> None:
        """Decode BIN payloads into t_data_values if they are not already present."""
        if self.connection is None:
            raise RuntimeError("No active connection. Use this method inside a 'with client as db' block.")

        table = self.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='t_data_values' LIMIT 1"
        ).fetchone()
        if table is not None:
            row_count = self.connection.execute("SELECT COUNT(*) FROM t_data_values").fetchone()[0]
            if row_count and int(row_count) > 0:
                return
            # Recover from stale/partial outputs where the table exists but is empty.
            self.connection.execute("DROP TABLE IF EXISTS t_data_values")

        with ZipFile(self.input_path, "r") as zf:
            _decode_bin_values(self.connection, zf)
        self.connection.commit()

    def __enter__(self) -> PLEXOS2SQLite:
        """Open connection and optionally decode and materialize derived tables."""
        if not self.output_path.exists():
            self.convert()
        self.connection = sqlite3.connect(str(self.output_path))
        if self.materialize_on_enter:
            self._ensure_data_values_decoded()
            _materialize_solution_tables(self.connection)
        else:
            _attach_solution_schemas(self.connection)
        return self

    def materialize_table(self, table: str, schema: str = "data") -> bool:
        """Materialize one derived table into the attached data/report schema.

        Returns True when the table was materialized, otherwise False.
        """
        import plexosdb.solution_reader as _sr

        if self.connection is None:
            raise RuntimeError("No active connection. Use this method inside a 'with client as db' block.")

        if schema not in {"data", "report"}:
            raise ValueError("schema must be 'data' or 'report'")

        # Fast path: if t_data_values is missing/empty, decode only key rows for this table.
        tdata_table = self.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='t_data_values' LIMIT 1"
        ).fetchone()
        has_full_data = False
        if tdata_table is not None:
            tdata_rows = self.connection.execute("SELECT COUNT(*) FROM t_data_values").fetchone()[0]
            has_full_data = bool(tdata_rows and int(tdata_rows) > 0)

        if not has_full_data:
            groups = _sr._build_derived_table_map(self.connection)
            key_ids = groups.get(("data", table))
            if not key_ids:
                return False

            self.connection.execute("DROP TABLE IF EXISTS temp._target_keys")
            self.connection.execute("CREATE TEMP TABLE _target_keys(key_id TEXT PRIMARY KEY)")
            self.connection.executemany(
                "INSERT OR IGNORE INTO _target_keys(key_id) VALUES (?)",
                [(str(int(k)),) for k in key_ids],
            )
            key_rows = self.connection.execute(
                """
                SELECT ki.key_id, ki.period_type_id, ki.length, ki.position, COALESCE(ki.period_offset, 0)
                FROM t_key_index ki
                JOIN temp._target_keys tk ON tk.key_id = CAST(ki.key_id AS TEXT)
                """
            ).fetchall()
            if not key_rows:
                return False

            with ZipFile(self.input_path, "r") as zf:
                return _sr._materialize_single_solution_table_from_subset(
                    self.connection,
                    table_name=table,
                    schema_name=schema,
                    key_rows=key_rows,
                    zf=zf,
                )

        return _sr._materialize_single_solution_table(self.connection, schema, table)

    def list_tables(self, schema: str = "data") -> list[str]:
        """Return names of all available derived tables for a given schema.

        Tables are derived from the solution metadata; they do not need to be
        materialized first. `report` mirrors `data` table names
        """
        if self.connection is None:
            raise RuntimeError("No active connection. Use this method inside a 'with client as db' block.")

        if schema not in {"data", "report"}:
            raise ValueError("schema must be 'data' or 'report'")

        groups = _build_derived_table_map(self.connection)
        if schema == "report":
            return sorted(name for (s, name) in groups if s == "data")
        return sorted(name for (s, name) in groups if s == schema)

    def _timestamp_block_names(self) -> list[str]:
        """List logical timestamp block names based on available phase/period tables."""
        if self.connection is None:
            return []
        table_names = {
            r[0] for r in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        period_map = {
            "Interval": "t_period_0",
            "Day": "t_period_1",
            "Year": "t_period_4",
        }
        phase_map = {
            "PASA": "t_phase_2",
            "MT": "t_phase_3",
            "ST": "t_phase_4",
        }
        names: list[str] = []
        for phase_name, phase_table in phase_map.items():
            if phase_table not in table_names:
                continue
            for period_name, period_table in period_map.items():
                if period_table in table_names:
                    names.append(f"timestamp_block_{phase_name}__{period_name}")
        return sorted(names)

    def _raw_table_names(self) -> list[str]:
        """Return logical raw table names exposed by the compatibility catalog."""
        # Raw object names.
        names = [
            "attribute_data",
            "attributes",
            "bands",
            "categories",
            "class_groups",
            "classes",
            "collections",
            "config",
            "custom_columns",
            "key_indexes",
            "keys",
            "memberships",
            "memo_objects",
            "models",
            "objects",
            "properties",
            "samples",
            "timeslices",
            "units",
        ]
        names.extend(self._timestamp_block_names())
        return sorted(set(names))

    def _processed_table_names(self) -> list[str]:
        """Return logical processed object names exposed as compatibility views."""
        names = [
            n for n in self._raw_table_names() if n in {"classes", "memberships", "objects", "properties"}
        ]
        names.extend(self._timestamp_block_names())
        return sorted(set(names))

    def list_catalog_tables(self) -> list[dict[str, str]]:
        """Return catalog of logical tables/views.

        Output rows include: table_catalog, table_schema, table_name, table_type.
        This is a compatibility view for tooling that expects
        schema layout (main/raw/processed/data/report).
        """
        if self.connection is None:
            raise RuntimeError("No active connection. Use this method inside a 'with client as db' block.")

        table_catalog = self.input_path.stem
        rows: list[dict[str, str]] = []

        # main
        rows.append(
            {
                "table_catalog": table_catalog,
                "table_schema": "main",
                "table_name": "plexos2sqlite",
                "table_type": "BASE TABLE",
            }
        )

        # raw + processed logical objects
        for table_name in self._raw_table_names():
            rows.append(
                {
                    "table_catalog": table_catalog,
                    "table_schema": "raw",
                    "table_name": table_name,
                    "table_type": "BASE TABLE",
                }
            )
        for table_name in self._processed_table_names():
            rows.append(
                {
                    "table_catalog": table_catalog,
                    "table_schema": "processed",
                    "table_name": table_name,
                    "table_type": "VIEW",
                }
            )

        # data/report derived tables
        for table_name in self.list_tables(schema="data"):
            rows.append(
                {
                    "table_catalog": table_catalog,
                    "table_schema": "data",
                    "table_name": table_name,
                    "table_type": "BASE TABLE",
                }
            )
            rows.append(
                {
                    "table_catalog": table_catalog,
                    "table_schema": "report",
                    "table_name": table_name,
                    "table_type": "VIEW",
                }
            )

        rows.sort(key=lambda r: (r["table_schema"], r["table_name"]))
        return rows

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        """Close the active SQLite connection on context manager exit."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
