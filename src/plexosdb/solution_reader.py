"""Utilities to import PLEXOS solution ZIP outputs into SQLite."""

from __future__ import annotations

import sqlite3
import struct
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any
from zipfile import ZipFile


def _quote_ident(identifier: str) -> str:
    escaped = identifier.replace('"', '""')
    return f'"{escaped}"'


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _coerce_value(value: str | None) -> int | float | str | None:
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


def _select_xml_entry(zip_path: Path, entries: list[str], model_name: str | None = None) -> str:
    xml_entries = [name for name in entries if name.lower().endswith(".xml")]
    if not xml_entries:
        raise FileNotFoundError("No XML file found in the solution ZIP.")

    stem = zip_path.stem
    for name in xml_entries:
        if Path(name).stem == stem:
            return name

    normalized_model_name = model_name.lower() if model_name else ""
    if normalized_model_name:
        for name in xml_entries:
            if normalized_model_name in Path(name).stem.lower():
                return name

    return xml_entries[0]


def _collect_xml_rows(xml_content: str) -> dict[str, list[dict[str, Any]]]:
    root = ET.fromstring(xml_content)
    rows_by_table: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for table_element in root:
        table_name = _local_name(table_element.tag)
        row: dict[str, Any] = {}
        for col in table_element:
            row[_local_name(col.tag)] = _coerce_value(col.text)
        rows_by_table[table_name].append(row)

    return rows_by_table


def _resolve_input_zip_path(input_path: str | Path) -> Path:
    path = Path(input_path)
    if path.is_file():
        if path.suffix.lower() != ".zip":
            raise ValueError(f"Input file must be a .zip solution file: {path}")
        return path
    if path.is_dir():
        zip_files = sorted(path.glob("*.zip"))
        if len(zip_files) == 1:
            return zip_files[0]
        if len(zip_files) == 0:
            raise FileNotFoundError(f"No .zip files found in directory: {path}")
        raise ValueError(f"Multiple .zip files found in directory: {path}")
    raise FileNotFoundError(f"Input path does not exist: {path}")


def _sanitize_name(value: str | None) -> str:
    if not value:
        return "Unknown"
    out = []
    prev_sep = False
    for ch in value.strip():
        if ch.isalnum():
            out.append(ch)
            prev_sep = False
        else:
            if not prev_sep:
                out.append("_")
                prev_sep = True
    return "".join(out).strip("_") or "Unknown"


def _period_type_name(period_type_id: int | None) -> str:
    mapping = {
        0: "Interval",
        1: "Day",
        2: "Week",
        3: "Month",
        4: "Year",
        6: "Hour",
        7: "Quarter",
    }
    if period_type_id is None:
        return "Period"
    return mapping.get(period_type_id, f"Period{period_type_id}")


# Maps period name (embedded in derived table name) → (period_table, id_col, datetime_col)
_PERIOD_TABLE_META: dict[str, tuple[str, str, str]] = {
    "Interval": ("t_period_0", "interval_id", "datetime"),
    "Day": ("t_period_1", "day_id", "date"),
    "Week": ("t_period_2", "week_id", "date"),
    "Month": ("t_period_3", "month_id", "date"),
    "Year": ("t_period_4", "fiscal_year_id", "year_ending"),
    "Hour": ("t_period_6", "hour_id", "datetime"),
    "Quarter": ("t_period_7", "quarter_id", "date"),
}


def _ensure_join_indexes(con: sqlite3.Connection, table_names: set[str]) -> None:
    """Create indexes required for fast JOIN-based rich materialization."""
    con.execute("CREATE INDEX IF NOT EXISTS idx_t_data_values_key_id ON t_data_values(key_id)")
    for tbl, col in [
        ("t_key", "key_id"),
        ("t_membership", "membership_id"),
        ("t_object", "object_id"),
        ("t_sample", "sample_id"),
    ]:
        if tbl in table_names:
            con.execute(f"CREATE INDEX IF NOT EXISTS idx_{tbl}_{col} ON {tbl}({col})")
    for period_table, id_col, _ in _PERIOD_TABLE_META.values():
        if period_table in table_names:
            con.execute(f"CREATE INDEX IF NOT EXISTS idx_{period_table}_{id_col} ON {period_table}({id_col})")


def _build_period_join(table_name: str, table_names: set[str]) -> tuple[str, str]:
    """Return (LEFT JOIN clause, datetime expression) for the period table matching this derived table
    name.
    """
    parts = table_name.split("__")
    if len(parts) >= 2:
        meta = _PERIOD_TABLE_META.get(parts[1])
        if meta:
            period_table, id_col, dt_col = meta
            if period_table in table_names:
                join = f"LEFT JOIN main.{period_table} p ON p.{id_col} = CAST(dv.block_id AS TEXT)"
                return join, f"p.{dt_col} AS datetime"
    return "", "NULL AS datetime"


def _build_rich_create_sql(
    schema_name: str,
    table_name: str,
    key_ids_sql: str,
    period_join: str,
    datetime_expr: str,
) -> str:
    """Return a CREATE TABLE AS SQL that embeds name/sample/band/datetime into the result."""
    sq = _quote_ident(schema_name)
    tq = _quote_ident(table_name)
    return f"""
        CREATE TABLE {sq}.{tq} AS
        SELECT
            o.name AS name,
            COALESCE(s.sample_name, 'Mean') AS sample_name,
            CAST(k.band_id AS INTEGER) AS band_id,
            dv.block_id,
            {datetime_expr},
            dv.value
        FROM main.t_data_values dv
        JOIN main.t_key k ON k.key_id = CAST(dv.key_id AS TEXT)
        LEFT JOIN main.t_sample s ON s.sample_id = k.sample_id
        LEFT JOIN main.t_membership m ON m.membership_id = k.membership_id
        LEFT JOIN main.t_object o ON o.object_id = m.child_object_id
        {period_join}
        WHERE dv.key_id IN ({key_ids_sql})
    """


def _build_fallback_create_sql(schema_name: str, table_name: str, key_ids_sql: str) -> str:
    """Minimal table without metadata joins, used when t_key/t_object/t_sample are absent."""
    sq = _quote_ident(schema_name)
    tq = _quote_ident(table_name)
    return f"""
        CREATE TABLE {sq}.{tq} AS
        SELECT dv.key_id, dv.period_type_id, dv.block_id, dv.value
        FROM main.t_data_values dv
        WHERE dv.key_id IN ({key_ids_sql})
    """


def _phase_name(phase_id: int, phase_ids: dict[str, set[int]]) -> str:
    if phase_id in phase_ids["ST"]:
        return "ST"
    if phase_id in phase_ids["MT"]:
        return "MT"
    if phase_id in phase_ids["PASA"]:
        return "PASA"
    if phase_id in phase_ids["LT"]:
        return "LT"
    # Default unresolved phase to ST to match common solution-table naming.
    return "ST"


def _table_columns(con: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()]


def _attached_db_names(con: sqlite3.Connection) -> set[str]:
    return {str(r[1]) for r in con.execute("PRAGMA database_list").fetchall()}


def _attach_solution_schemas(con: sqlite3.Connection) -> None:
    attached = _attached_db_names(con)
    if "data" not in attached:
        con.execute("ATTACH DATABASE ':memory:' AS data")
    if "report" not in attached:
        con.execute("ATTACH DATABASE ':memory:' AS report")


def _build_key_period_map(
    con: sqlite3.Connection,
    *,
    has_key_period: bool,
    key_index_cols: list[str],
) -> dict[int, int | None]:
    key_period: dict[int, int | None] = {}
    # Prefer t_key_index period_type_id. In many solution schemas this is the
    # authoritative period series used for value decoding, while t_key
    # period_type_id may be a coarse flag (e.g., 0/1).
    if "period_type_id" in key_index_cols:
        sql = "SELECT key_id, period_type_id FROM t_key_index"
    elif has_key_period:
        sql = "SELECT key_id, period_type_id FROM t_key"
    else:
        return key_period

    for key_id, period_type_id in con.execute(sql).fetchall():
        key_id_int = int(key_id)
        if key_id_int in key_period:
            continue
        key_period[key_id_int] = int(period_type_id) if period_type_id is not None else None
    return key_period


def _build_property_map(con: sqlite3.Connection, *, has_summary_name: bool) -> dict[int, tuple[str, str]]:
    if has_summary_name:
        prop_rows = con.execute(
            "SELECT property_id, name, COALESCE(summary_name, '') FROM t_property"
        ).fetchall()
        return {int(pid): (str(name), str(summary_name)) for pid, name, summary_name in prop_rows}

    prop_rows = con.execute("SELECT property_id, name FROM t_property").fetchall()
    return {int(pid): (str(name), "") for pid, name in prop_rows}


def _build_phase_sets(con: sqlite3.Connection, table_names: set[str]) -> dict[str, set[int]]:
    phase_ids = {"LT": set(), "PASA": set(), "MT": set(), "ST": set()}
    phase_table_to_name = {
        "t_phase_1": "LT",
        "t_phase_2": "PASA",
        "t_phase_3": "MT",
        "t_phase_4": "ST",
    }
    for table, pname in phase_table_to_name.items():
        if table not in table_names:
            continue
        phase_cols = _table_columns(con, table)
        id_col = next((c for c in ("phase_id", "period_id", "interval_id") if c in phase_cols), None)
        if id_col is None:
            continue
        for (v,) in con.execute(f"SELECT {id_col} FROM {table}").fetchall():
            if v is None:
                continue
            try:
                phase_ids[pname].add(int(v))
            except (TypeError, ValueError):
                continue
    return phase_ids


def _build_derived_table_map(con: sqlite3.Connection) -> dict[tuple[str, str], set[int]]:
    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    required = {"t_key", "t_key_index", "t_property", "t_membership", "t_collection"}
    if not required.issubset(table_names):
        return {}

    key_cols = _table_columns(con, "t_key")
    key_index_cols = _table_columns(con, "t_key_index")
    property_cols = _table_columns(con, "t_property")

    has_summary = "is_summary" in key_cols
    has_phase = "phase_id" in key_cols
    has_key_period = "period_type_id" in key_cols
    has_summary_name = "summary_name" in property_cols

    key_select = ["key_id", "property_id", "membership_id"]
    if has_summary:
        key_select.append("is_summary")
    if has_phase:
        key_select.append("phase_id")
    key_rows = con.execute(f"SELECT {', '.join(key_select)} FROM t_key").fetchall()

    key_period = _build_key_period_map(
        con,
        has_key_period=has_key_period,
        key_index_cols=key_index_cols,
    )

    property_map = _build_property_map(con, has_summary_name=has_summary_name)

    membership_collection = {
        int(mid): int(cid)
        for mid, cid in con.execute("SELECT membership_id, collection_id FROM t_membership").fetchall()
    }
    collection_map = {
        int(cid): str(name)
        for cid, name in con.execute("SELECT collection_id, name FROM t_collection").fetchall()
    }

    phase_ids = _build_phase_sets(con, table_names)

    groups: dict[tuple[str, str], set[int]] = defaultdict(set)
    for row in key_rows:
        key_id = int(row[0])
        property_id = int(row[1])
        membership_id = int(row[2])
        is_summary = bool(int(row[3])) if has_summary and row[3] is not None else False
        phase_id = int(row[4]) if has_phase and len(row) > 4 and row[4] is not None else -1

        period_name = _period_type_name(key_period.get(key_id))
        phase_name = _phase_name(phase_id, phase_ids) if phase_id != -1 else "ST"
        collection_name = collection_map.get(membership_collection.get(membership_id, -1), "Collection")
        prop_name, summary_name = property_map.get(property_id, ("Property", ""))

        schema_name = "report" if is_summary else "data"
        selected_prop = summary_name if is_summary and summary_name else prop_name
        table_name = "__".join(
            [
                _sanitize_name(phase_name),
                _sanitize_name(period_name),
                _sanitize_name(collection_name),
                _sanitize_name(selected_prop),
            ]
        )
        groups[(schema_name, table_name)].add(key_id)

    return groups


def _materialize_solution_tables(con: sqlite3.Connection) -> None:
    _attach_solution_schemas(con)

    groups = _build_derived_table_map(con)
    if not groups:
        return

    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    has_meta = {"t_key", "t_sample", "t_membership", "t_object"}.issubset(table_names)
    _ensure_join_indexes(con, table_names)

    for (schema_name, table_name), key_ids in groups.items():
        if not key_ids:
            continue
        key_ids_sql = ",".join(str(int(k)) for k in sorted(key_ids))
        con.execute(f"DROP TABLE IF EXISTS {_quote_ident(schema_name)}.{_quote_ident(table_name)}")
        if has_meta:
            period_join, datetime_expr = _build_period_join(table_name, table_names)
            sql = _build_rich_create_sql(schema_name, table_name, key_ids_sql, period_join, datetime_expr)
        else:
            sql = _build_fallback_create_sql(schema_name, table_name, key_ids_sql)
        con.execute(sql)


def _materialize_single_solution_table(
    con: sqlite3.Connection,
    schema_name: str,
    table_name: str,
) -> bool:
    _attach_solution_schemas(con)
    groups = _build_derived_table_map(con)
    key_ids = groups.get((schema_name, table_name))
    if not key_ids:
        return False

    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    has_meta = {"t_key", "t_sample", "t_membership", "t_object"}.issubset(table_names)
    _ensure_join_indexes(con, table_names)

    key_ids_sql = ",".join(str(int(k)) for k in sorted(key_ids))
    con.execute(f"DROP TABLE IF EXISTS {_quote_ident(schema_name)}.{_quote_ident(table_name)}")
    if has_meta:
        period_join, datetime_expr = _build_period_join(table_name, table_names)
        sql = _build_rich_create_sql(schema_name, table_name, key_ids_sql, period_join, datetime_expr)
    else:
        sql = _build_fallback_create_sql(schema_name, table_name, key_ids_sql)
    con.execute(sql)
    return True


def _create_and_insert_rows(con: sqlite3.Connection, table: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    all_cols: list[str] = sorted({col for row in rows for col in row})
    col_defs = ", ".join(f"{_quote_ident(col)} TEXT" for col in all_cols)
    con.execute(f"CREATE TABLE IF NOT EXISTS {_quote_ident(table)} ({col_defs})")

    placeholders = ", ".join("?" for _ in all_cols)
    col_sql = ", ".join(_quote_ident(col) for col in all_cols)
    values = [tuple(row.get(col) for col in all_cols) for row in rows]
    con.executemany(
        f"INSERT INTO {_quote_ident(table)} ({col_sql}) VALUES ({placeholders})",
        values,
    )


def _read_all_bin_entries(zf: ZipFile) -> dict[int, bytes]:
    period_bytes: dict[int, bytes] = {}
    for name in zf.namelist():
        lower_name = name.lower()
        if not lower_name.startswith("t_data_") or not lower_name.endswith(".bin"):
            continue
        suffix = lower_name[len("t_data_") : -len(".bin")]
        try:
            period_type_id = int(suffix)
        except ValueError:
            continue
        period_bytes[period_type_id] = zf.read(name)
    return period_bytes


def _bin_entry_name_map(zf: ZipFile) -> dict[int, str]:
    """Map period_type_id -> ZIP entry name for t_data_<id>.BIN files."""
    names: dict[int, str] = {}
    for name in zf.namelist():
        lower_name = name.lower()
        if not lower_name.startswith("t_data_") or not lower_name.endswith(".bin"):
            continue
        suffix = lower_name[len("t_data_") : -len(".bin")]
        try:
            period_type_id = int(suffix)
        except ValueError:
            continue
        names[period_type_id] = name
    return names


def _skip_bytes(stream: Any, nbytes: int) -> bool:
    """Advance a stream by nbytes, returning False if EOF is reached early."""
    remaining = nbytes
    chunk_size = 1024 * 1024
    while remaining > 0:
        chunk = stream.read(min(chunk_size, remaining))
        if not chunk:
            return False
        remaining -= len(chunk)
    return True


def _group_key_rows_by_period(
    key_rows: list[tuple[Any, Any, Any, Any, Any]],
    period_entries: dict[int, str],
) -> dict[int, list[tuple[int, int, int, int]]]:
    rows_by_period: dict[int, list[tuple[int, int, int, int]]] = defaultdict(list)
    for key_id, period_type_id, length, position, period_offset in key_rows:
        try:
            period_type = int(period_type_id)
            num_values = int(length)
            byte_pos = int(position)
            offset = int(period_offset)
            key_id_int = int(key_id)
        except (TypeError, ValueError):
            continue

        if period_type not in period_entries or num_values <= 0:
            continue

        rows_by_period[period_type].append((key_id_int, num_values, byte_pos, offset))

    return rows_by_period


def _decode_period_rows(
    zf: ZipFile,
    entry_name: str,
    period_type: int,
    rows: list[tuple[int, int, int, int]],
) -> list[tuple[int, int, int, float]]:
    out_rows: list[tuple[int, int, int, float]] = []

    # Read keys in byte-order to minimize stream movement and memory overhead.
    sorted_rows = sorted(rows, key=lambda x: x[2])
    with zf.open(entry_name, "r") as stream:
        current_pos = 0
        for key_id, num_values, byte_pos, offset in sorted_rows:
            if byte_pos < current_pos:
                # Defensive fallback for unexpected non-monotonic positions.
                try:
                    stream.seek(byte_pos)
                    current_pos = byte_pos
                except Exception:
                    continue

            if byte_pos > current_pos:
                ok = _skip_bytes(stream, byte_pos - current_pos)
                if not ok:
                    continue
                current_pos = byte_pos

            byte_len = num_values * 8
            chunk = stream.read(byte_len)
            if len(chunk) != byte_len:
                continue
            current_pos += byte_len

            values = struct.unpack(f"<{num_values}d", chunk)
            for idx, value in enumerate(values):
                block_id = offset + idx + 1
                out_rows.append((key_id, period_type, block_id, float(value)))

    return out_rows


def _decode_bin_values(con: sqlite3.Connection, zf: ZipFile) -> None:
    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "t_key_index" not in table_names:
        return

    key_rows = con.execute(
        "SELECT key_id, period_type_id, length, position, COALESCE(period_offset, 0) FROM t_key_index"
    ).fetchall()
    if not key_rows:
        return

    period_entries = _bin_entry_name_map(zf)
    if not period_entries:
        return

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS t_data_values (
            key_id INTEGER NOT NULL,
            period_type_id INTEGER NOT NULL,
            block_id INTEGER NOT NULL,
            value REAL NOT NULL
        )
        """
    )

    rows_by_period = _group_key_rows_by_period(key_rows, period_entries)

    if not rows_by_period:
        return

    insert_sql = "INSERT INTO t_data_values(key_id, period_type_id, block_id, value) VALUES (?, ?, ?, ?)"
    batch: list[tuple[int, int, int, float]] = []
    batch_size = 100_000

    for period_type, rows in rows_by_period.items():
        entry_name = period_entries.get(period_type)
        if entry_name is None:
            continue

        period_batch = _decode_period_rows(zf, entry_name, period_type, rows)
        for row in period_batch:
            batch.append(row)
            if len(batch) >= batch_size:
                con.executemany(insert_sql, batch)
                batch.clear()

    if batch:
        con.executemany(insert_sql, batch)


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
        xml_content = zf.read(xml_entry).decode("utf-8-sig")
        rows_by_table = _collect_xml_rows(xml_content)

        for table, rows in rows_by_table.items():
            _create_and_insert_rows(con, table, rows)

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
            return

        with ZipFile(self.input_path, "r") as zf:
            _decode_bin_values(self.connection, zf)
        self.connection.commit()

    def __enter__(self) -> PLEXOS2SQLite:
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
        if self.connection is None:
            raise RuntimeError("No active connection. Use this method inside a 'with client as db' block.")

        if schema not in {"data", "report"}:
            raise ValueError("schema must be 'data' or 'report'")

        self._ensure_data_values_decoded()
        return _materialize_single_solution_table(self.connection, schema, table)

    def list_tables(self, schema: str = "data") -> list[str]:
        """Return names of all available derived tables for a given schema.

        Tables are derived from the solution metadata; they do not need to be
        materialized first.  Use schema='data' for interval/period results and
        schema='report' for summary results.
        """
        if self.connection is None:
            raise RuntimeError("No active connection. Use this method inside a 'with client as db' block.")

        if schema not in {"data", "report"}:
            raise ValueError("schema must be 'data' or 'report'")

        groups = _build_derived_table_map(self.connection)
        return sorted(name for (s, name) in groups if s == schema)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
