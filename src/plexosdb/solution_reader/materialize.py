"""Derived-table naming, materialization, and report schema management."""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from typing import Any
from zipfile import ZipFile

from .utils import _quote_ident


def _sanitize_name(value: str | None) -> str:
    """Normalize free-form names to underscore-separated alphanumeric tokens."""
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


def _table_label_part(value: str | None) -> str:
    """Match label formatting for table name parts.

    Keep symbols like '&' and only normalize spaces/hyphens to underscores.
    """
    if not value:
        return "Unknown"
    part = value.strip().replace(" ", "_").replace("-", "_")
    return part or "Unknown"


def _period_type_name(period_type_id: int | None) -> str:
    """Map a period type id to a canonical period label."""
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
    if "t_data_values" in table_names:
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
    dv_source: str = "main.t_data_values",
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
        FROM {dv_source} dv
        JOIN main.t_key k ON k.key_id = CAST(dv.key_id AS TEXT)
        LEFT JOIN main.t_sample s ON s.sample_id = k.sample_id
        LEFT JOIN main.t_membership m ON m.membership_id = k.membership_id
        LEFT JOIN main.t_object o ON o.object_id = m.child_object_id
        {period_join}
        WHERE dv.key_id IN ({key_ids_sql})
    """


def _build_fallback_create_sql(
    schema_name: str,
    table_name: str,
    key_ids_sql: str,
    dv_source: str = "main.t_data_values",
) -> str:
    """Minimal table without metadata joins, used when t_key/t_object/t_sample are absent."""
    sq = _quote_ident(schema_name)
    tq = _quote_ident(table_name)
    return f"""
        CREATE TABLE {sq}.{tq} AS
        SELECT dv.key_id, dv.period_type_id, dv.block_id, dv.value
        FROM {dv_source} dv
        WHERE dv.key_id IN ({key_ids_sql})
    """


def _phase_name(phase_id: int, phase_ids: dict[str, set[int]]) -> str:
    """Resolve a numeric phase id to LT/PASA/MT/ST with ST fallback."""
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
    """Return column names for a SQLite table."""
    return [r[1] for r in con.execute(f"PRAGMA table_info({table})").fetchall()]


def _attached_db_names(con: sqlite3.Connection) -> set[str]:
    """Return names of databases currently attached to the connection."""
    return {str(r[1]) for r in con.execute("PRAGMA database_list").fetchall()}


def _attach_solution_schemas(con: sqlite3.Connection) -> None:
    """Attach in-memory data and report schemas if they are not present."""
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
    """Build key_id to period_type_id mapping from available key tables."""
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
    """Build property_id to (name, summary_name) mapping."""
    if has_summary_name:
        prop_rows = con.execute(
            "SELECT property_id, name, COALESCE(summary_name, '') FROM t_property"
        ).fetchall()
        return {int(pid): (str(name), str(summary_name)) for pid, name, summary_name in prop_rows}

    prop_rows = con.execute("SELECT property_id, name FROM t_property").fetchall()
    return {int(pid): (str(name), "") for pid, name in prop_rows}


def _build_phase_sets(con: sqlite3.Connection, table_names: set[str]) -> dict[str, set[int]]:
    """Collect phase ids grouped by phase label from available phase tables.

    ``t_key.phase_id`` encodes the PLEXOS phase type directly (1=LT, 2=PASA,
    3=MT, 4=ST).  When a phase table has a ``phase_id`` column we read its
    values (some solution formats store the type id there explicitly).  When
    the table only has period/interval columns — which are sequential period
    identifiers, not phase types — we fall back to the table number itself
    (e.g. ``t_phase_4`` → type ``4``).  Mixing ``period_id`` into the lookup
    set would cause false matches against ``t_key.phase_id``.
    """
    phase_ids: dict[str, set[int]] = {"LT": set(), "PASA": set(), "MT": set(), "ST": set()}
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
        if "phase_id" in phase_cols:
            # Explicit phase_id column — read actual values.
            for (v,) in con.execute(f"SELECT phase_id FROM {table}").fetchall():
                if v is None:
                    continue
                try:
                    phase_ids[pname].add(int(v))
                except (TypeError, ValueError):
                    continue
        elif "period_id" in phase_cols or "interval_id" in phase_cols:
            # No phase_id column but has period/interval columns: sequential
            # period numbers, not phase types.  Use the table number instead.
            table_number = int(table.rsplit("_", 1)[-1])
            phase_ids[pname].add(table_number)
    return phase_ids


def _build_derived_table_map(con: sqlite3.Connection) -> dict[tuple[str, str], set[int]]:
    """Map derived data-table names to the key ids that populate each table."""
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
    key_select.append("phase_id" if has_phase else "NULL AS phase_id")
    key_select.append("is_summary" if has_summary else "NULL AS is_summary")
    key_select.append("period_type_id" if has_key_period else "NULL AS key_period_type_id")
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
        phase_id = int(row[3]) if row[3] is not None else -1

        # Prefer explicit key.is_summary when present; otherwise infer from key.period_type_id.
        if row[4] is not None:
            is_summary = bool(int(row[4]))
        elif row[5] is not None:
            is_summary = int(row[5]) == 1
        else:
            is_summary = False

        period_name = _period_type_name(key_period.get(key_id))
        phase_name = _phase_name(phase_id, phase_ids) if phase_id != -1 else "ST"
        collection_name = collection_map.get(membership_collection.get(membership_id, -1), "Collection")
        prop_name, summary_name = property_map.get(property_id, ("Property", ""))

        selected_prop = summary_name if is_summary and summary_name else prop_name
        table_name = "__".join(
            [
                _table_label_part(phase_name),
                _table_label_part(period_name),
                _table_label_part(collection_name),
                _table_label_part(selected_prop),
            ]
        )
        groups[("data", table_name)].add(key_id)

    return groups


def _report_interval_length(table_name: str) -> int | None:
    """Return interval length in hours inferred from a derived table name."""
    parts = table_name.split("__")
    if len(parts) < 2:
        return None
    return {
        "Interval": 1,
        "Hour": 1,
        "Day": 24,
        "Week": 168,
        "Month": 730,
        "Quarter": 2190,
        "Year": 8760,
    }.get(parts[1])


def _resolve_report_unit(
    con: sqlite3.Connection,
    *,
    key_ids: set[int],
) -> str | None:
    """Resolve display unit text for a report table from key/property metadata."""
    if not key_ids:
        return None
    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    required = {"t_key", "t_property", "t_unit"}
    if not required.issubset(table_names):
        return None

    key_cols = set(_table_columns(con, "t_key"))
    has_is_summary = "is_summary" in key_cols
    key_ids_sql = ",".join(str(int(k)) for k in sorted(key_ids))
    if has_is_summary:
        unit_expr = """
            COALESCE(
                CASE
                    WHEN COALESCE(CAST(k.is_summary AS INTEGER), 0) = 1
                    THEN pu_summary.value
                    ELSE pu.value
                END,
                pu.value
            )
        """
    else:
        unit_expr = "COALESCE(pu.value, pu_summary.value)"

    row = con.execute(
        f"""
        SELECT
            {unit_expr} AS unit_text
        FROM t_key k
        JOIN t_property p ON p.property_id = k.property_id
        LEFT JOIN t_unit pu ON pu.unit_id = p.unit_id
        LEFT JOIN t_unit pu_summary ON pu_summary.unit_id = p.summary_unit_id
        WHERE k.key_id IN ({key_ids_sql})
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        return None
    unit = row[0]
    return str(unit) if unit is not None else None


def _copy_data_table_to_report(con: sqlite3.Connection, table_name: str, *, key_ids: set[int]) -> None:
    """Create report-style table from data table, with fallback to plain mirror."""
    tq = _quote_ident(table_name)
    value_col = _quote_ident(table_name.split("__")[-1] if "__" in table_name else "value")
    interval_length = _report_interval_length(table_name)
    interval_sql = "NULL" if interval_length is None else str(interval_length)
    unit_text = _resolve_report_unit(con, key_ids=key_ids)
    if unit_text is None:
        unit_sql = "NULL"
    else:
        unit_sql = "'" + unit_text.replace("'", "''") + "'"
    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    table_name_escaped = table_name.replace('"', '""')
    data_cols = {r[1] for r in con.execute(f'PRAGMA data.table_info("{table_name_escaped}")').fetchall()}

    con.execute(f"DROP TABLE IF EXISTS report.{tq}")
    required_data_cols = {"band_id", "sample_name", "name", "datetime", "value"}
    if {"t_object", "t_category"}.issubset(table_names) and required_data_cols.issubset(data_cols):
        con.execute(
            f"""
            CREATE TABLE report.{tq} AS
            SELECT
                d.band_id AS band,
                d.sample_name AS sample_name,
                d.name AS name,
                c.name AS category,
                CASE
                    WHEN d.datetime IS NULL THEN NULL
                    WHEN INSTR(d.datetime, '/') > 0
                        THEN SUBSTR(d.datetime, 7, 4) || '-' || SUBSTR(d.datetime, 4, 2) || '-' ||
                             SUBSTR(d.datetime, 1, 2) || ' ' || SUBSTR(d.datetime, 12, 8)
                    WHEN INSTR(d.datetime, 'T') > 0 THEN REPLACE(SUBSTR(d.datetime, 1, 19), 'T', ' ')
                    ELSE d.datetime
                END AS timestamp,
                {interval_sql} AS interval_length,
                d.value AS {value_col},
                {unit_sql} AS unit
            FROM data.{tq} d
            LEFT JOIN t_object o ON o.name = d.name
            LEFT JOIN t_category c ON c.category_id = o.category_id
            """
        )
        return

    con.execute(f"CREATE TABLE report.{tq} AS SELECT * FROM data.{tq}")


def _materialize_solution_tables(con: sqlite3.Connection) -> None:
    """Materialize all derived data and report tables in attached schemas."""
    import plexosdb.solution_reader as _sr

    _attach_solution_schemas(con)

    groups = _sr._build_derived_table_map(con)
    if not groups:
        return

    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    has_meta = {"t_key", "t_sample", "t_membership", "t_object"}.issubset(table_names)
    _sr._ensure_join_indexes(con, table_names)

    for (schema_name, table_name), key_ids in groups.items():
        if not key_ids:
            continue
        key_ids_sql = ",".join(str(int(k)) for k in sorted(key_ids))
        con.execute(f"DROP TABLE IF EXISTS {_quote_ident(schema_name)}.{_quote_ident(table_name)}")
        if has_meta:
            period_join, datetime_expr = _build_period_join(table_name, table_names)
            sql = _build_rich_create_sql(schema_name, table_name, key_ids_sql, period_join, datetime_expr)
        else:
            sql = _sr._build_fallback_create_sql(schema_name, table_name, key_ids_sql)
        con.execute(sql)
        _sr._copy_data_table_to_report(con, table_name, key_ids=key_ids)


def _materialize_single_solution_table(
    con: sqlite3.Connection,
    schema_name: str,
    table_name: str,
) -> bool:
    """Materialize one derived table into data and synchronized report schema."""
    import plexosdb.solution_reader as _sr

    _attach_solution_schemas(con)
    groups = _sr._build_derived_table_map(con)
    key_ids = groups.get(("data", table_name))
    if not key_ids:
        return False

    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    has_meta = {"t_key", "t_sample", "t_membership", "t_object"}.issubset(table_names)
    _sr._ensure_join_indexes(con, table_names)

    key_ids_sql = ",".join(str(int(k)) for k in sorted(key_ids))
    con.execute(f"DROP TABLE IF EXISTS data.{_quote_ident(table_name)}")
    if has_meta:
        period_join, datetime_expr = _build_period_join(table_name, table_names)
        sql = _build_rich_create_sql("data", table_name, key_ids_sql, period_join, datetime_expr)
    else:
        sql = _sr._build_fallback_create_sql("data", table_name, key_ids_sql)
    con.execute(sql)
    if schema_name == "report":
        _sr._copy_data_table_to_report(con, table_name, key_ids=key_ids)
    else:
        # Keep report schema in sync with data-table availability.
        _sr._copy_data_table_to_report(con, table_name, key_ids=key_ids)
    return True


def _materialize_single_solution_table_from_subset(
    con: sqlite3.Connection,
    *,
    table_name: str,
    schema_name: str,
    key_rows: list[tuple[Any, Any, Any, Any, Any]],
    zf: ZipFile,
) -> bool:
    """Materialize one table using only key rows for that table.

    This path avoids decoding all solution values when only one derived table is requested.
    """
    import plexosdb.solution_reader as _sr

    _attach_solution_schemas(con)
    groups = _sr._build_derived_table_map(con)
    key_ids = groups.get(("data", table_name))
    if not key_ids:
        return False

    period_entries = _sr._bin_entry_name_map(zf)
    if not period_entries:
        return False
    rows_by_period = _sr._group_key_rows_by_period(key_rows, period_entries)
    if not rows_by_period:
        return False

    con.execute("DROP TABLE IF EXISTS temp._dv_subset")
    con.execute(
        """
        CREATE TEMP TABLE _dv_subset (
            key_id INTEGER NOT NULL,
            period_type_id INTEGER NOT NULL,
            block_id INTEGER NOT NULL,
            value REAL NOT NULL
        )
        """
    )
    insert_sql = "INSERT INTO temp._dv_subset(key_id, period_type_id, block_id, value) VALUES (?, ?, ?, ?)"
    batch: list[tuple[int, int, int, float]] = []
    batch_size = 100_000
    for period_type, rows in rows_by_period.items():
        entry_name = period_entries.get(period_type)
        if entry_name is None:
            continue
        for row in _sr._decode_period_rows(zf, entry_name, period_type, rows):
            batch.append(row)
            if len(batch) >= batch_size:
                con.executemany(insert_sql, batch)
                batch.clear()
    if batch:
        con.executemany(insert_sql, batch)
    con.execute("CREATE INDEX IF NOT EXISTS temp.idx_dv_subset_key_id ON _dv_subset(key_id)")

    table_names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    has_meta = {"t_key", "t_sample", "t_membership", "t_object"}.issubset(table_names)
    _sr._ensure_join_indexes(con, table_names)

    key_ids_sql = ",".join(str(int(k)) for k in sorted(key_ids))
    con.execute(f"DROP TABLE IF EXISTS data.{_quote_ident(table_name)}")
    if has_meta:
        period_join, datetime_expr = _build_period_join(table_name, table_names)
        sql = _build_rich_create_sql(
            "data",
            table_name,
            key_ids_sql,
            period_join,
            datetime_expr,
            dv_source="temp._dv_subset",
        )
    else:
        sql = _sr._build_fallback_create_sql("data", table_name, key_ids_sql, dv_source="temp._dv_subset")
    con.execute(sql)
    _sr._copy_data_table_to_report(con, table_name, key_ids=key_ids)
    return True
