"""Internal helpers for the DuckDB-backed solution wrapper."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import duckdb
from plexos2duckdb import PLEXOS2DuckDB

from .db_solution_models import (
    DuckDBSchema,
    IfExists,
    ResultPeriod,
    ResultPhase,
    ResultSchema,
    ResultTable,
    TableType,
)
from .enums import (
    ClassEnum,
    CollectionEnum,
    get_default_collection,
    parse_class_enum,
    parse_collection_enum,
)
from .utils import normalize_names


def open_solution_connection(
    source_path: Path,
    database: str | Path | None,
    *,
    if_exists: IfExists,
    n_threads: int | None,
    table_name_pattern: str | None,
    in_memory: bool,
) -> tuple[duckdb.DuckDBPyConnection, Path | None]:
    """Convert or reuse a solution database and return an open DuckDB connection."""
    if in_memory:
        if database is not None:
            raise ValueError("database must be None when in_memory=True")
        with TemporaryDirectory() as tmpdir:
            temp_database = Path(tmpdir) / f"{source_path.stem}.duckdb"
            convert_solution_to_duckdb(
                source_path,
                temp_database,
                if_exists="replace",
                n_threads=n_threads,
                table_name_pattern=table_name_pattern,
            )
            connection = copy_duckdb_to_memory(temp_database)
        return connection, None

    duckdb_path = Path(database) if database is not None else source_path.with_suffix(".duckdb")
    converted_path = convert_solution_to_duckdb(
        source_path,
        duckdb_path,
        if_exists=if_exists,
        n_threads=n_threads,
        table_name_pattern=table_name_pattern,
    )
    return duckdb.connect(str(converted_path), read_only=True), converted_path


def convert_solution_to_duckdb(
    source_path: Path,
    database: Path,
    *,
    if_exists: IfExists,
    n_threads: int | None,
    table_name_pattern: str | None,
) -> Path:
    """Convert *source_path* to *database*, respecting the requested overwrite policy."""
    if database.exists():
        if if_exists == "fail":
            raise FileExistsError(f"Output file already exists: {database}")
        if if_exists == "reuse":
            return database

    client = PLEXOS2DuckDB(source_path, output_path=database)
    return client.convert(
        force=if_exists == "replace",
        n_threads=n_threads,
        table_name_pattern=table_name_pattern,
    )


def copy_duckdb_to_memory(database: Path) -> duckdb.DuckDBPyConnection:
    """Copy a file-backed DuckDB database into a new in-memory DuckDB connection."""
    connection = duckdb.connect(":memory:")
    attach_path = str(database).replace("'", "''")
    try:
        connection.execute(f"ATTACH '{attach_path}' AS source_db (READ_ONLY)")
        connection.execute("COPY FROM DATABASE source_db TO memory")
        connection.execute("DETACH source_db")
    except Exception:
        connection.close()
        raise
    return connection


def solution_table_names(connection: duckdb.DuckDBPyConnection, *, schema: DuckDBSchema) -> list[str]:
    """Return table names for one schema in the current DuckDB database."""
    rows = connection.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_catalog = current_database()
          AND table_schema = ?
        ORDER BY table_name
        """,
        (schema,),
    ).fetchall()
    return [str(row[0]) for row in rows]


def solution_metadata_value(connection: duckdb.DuckDBPyConnection | None, key: str) -> str | None:
    """Return one value from the plexos2duckdb metadata table, when available."""
    if connection is None:
        return None
    try:
        row = connection.execute(
            "SELECT value FROM main.plexos2duckdb WHERE key = ?",
            (key,),
        ).fetchone()
    except duckdb.Error:
        return None
    return str(row[0]) if row is not None and row[0] is not None else None


def solution_metadata_source(connection: duckdb.DuckDBPyConnection | None) -> Path | None:
    """Return the source solution path recorded in DuckDB metadata, when available."""
    source = solution_metadata_value(connection, "plexos_file")
    return Path(source) if source else None


def sql_relation(connection: duckdb.DuckDBPyConnection, query_string: str) -> duckdb.DuckDBPyRelation:
    """Build a lazy DuckDB relation from a SQL query."""
    return connection.sql(query_string)


def query_rows(
    connection: duckdb.DuckDBPyConnection,
    query_string: str,
    params: tuple[Any, ...] | dict[str, Any] | None = None,
) -> list[Any]:
    """Execute a read-only query and return all rows."""
    validate_read_query(query_string)
    return list(connection.execute(query_string, params or []).fetchall())


def query_dict_rows(
    connection: duckdb.DuckDBPyConnection,
    query_string: str,
    params: tuple[Any, ...] | dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute a read-only query and return rows as dictionaries."""
    validate_read_query(query_string)
    cursor = connection.execute(query_string, params or [])
    columns = [desc[0] for desc in cursor.description or []]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def table_relation(
    connection: duckdb.DuckDBPyConnection,
    table: str | ResultTable,
    *,
    schema: DuckDBSchema = "report",
) -> duckdb.DuckDBPyRelation:
    """Build a lazy relation for a solution table or view."""
    if isinstance(table, ResultTable):
        table_name = table.name
        schema_name = table.schema
    else:
        table_name = table
        schema_name = schema
    return connection.sql(f"SELECT * FROM {quote_qualified_table(schema_name, table_name)}")


def list_solution_objects_by_class(
    connection: duckdb.DuckDBPyConnection,
    class_enum: ClassEnum | str,
    *,
    category: str | None = None,
) -> list[str]:
    """Return solution object names for a PLEXOS class."""
    parsed_class = parse_class_enum(class_enum)
    conditions = ['"class" = ?']
    params: list[Any] = [parsed_class.value]
    if category is not None:
        conditions.append("category = ?")
        params.append(category)
    where_clause = " AND ".join(conditions)
    rows = connection.execute(
        f"""
        SELECT name
        FROM processed.objects
        WHERE {where_clause}
        ORDER BY name
        """,
        params,
    ).fetchall()
    return [str(row[0]) for row in rows]


def list_solution_result_tables(
    connection: duckdb.DuckDBPyConnection,
    *,
    schema: ResultSchema = "report",
    phase: ResultPhase | str | None = None,
    period: ResultPeriod | str | None = None,
    class_enum: ClassEnum | str | None = None,
    collection: CollectionEnum | str | None = None,
    property_name: str | None = None,
) -> list[ResultTable]:
    """List result tables using PLEXOS class, collection, and property filters."""
    validate_result_schema(schema)
    parsed_phase = normalize_result_phase(phase) if phase is not None else None
    parsed_period = normalize_result_period(period) if period is not None else None
    parsed_class = parse_class_enum(class_enum) if class_enum is not None else None
    parsed_collection = normalize_collection(collection) if collection is not None else None
    if parsed_collection is None and parsed_class is not None:
        parsed_collection = get_default_collection(parsed_class)

    property_map = result_property_name_map(connection)
    rows = connection.execute(
        """
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_catalog = current_database()
          AND table_schema = ?
        ORDER BY table_name
        """,
        (schema,),
    ).fetchall()

    result: list[ResultTable] = []
    for table_name, table_type in rows:
        table = parse_result_table_name(
            str(table_name),
            schema=schema,
            table_type=str(table_type),
            property_map=property_map,
        )
        if table is None:
            continue
        if parsed_phase is not None and table.phase != parsed_phase:
            continue
        if parsed_period is not None and table.period != parsed_period:
            continue
        if parsed_class is not None and table.class_enum != parsed_class:
            continue
        if parsed_collection is not None and not collection_matches(table.collection, parsed_collection):
            continue
        if property_name is not None and table_label(property_name) != table_label(table.property_name):
            continue
        result.append(table)
    return result


def get_solution_result_table(
    connection: duckdb.DuckDBPyConnection,
    *,
    schema: ResultSchema = "report",
    phase: ResultPhase | str = ResultPhase.ST,
    period: ResultPeriod | str = ResultPeriod.INTERVAL,
    class_enum: ClassEnum | str | None = None,
    collection: CollectionEnum | str | None = None,
    property_name: str,
) -> ResultTable:
    """Return one result table matching PLEXOS dimensions."""
    matches = list_solution_result_tables(
        connection,
        schema=schema,
        phase=phase,
        period=period,
        class_enum=class_enum,
        collection=collection,
        property_name=property_name,
    )
    if not matches:
        raise KeyError(
            "No result table matched "
            f"schema={schema!r}, phase={phase!r}, period={period!r}, "
            f"class_enum={class_enum!r}, collection={collection!r}, property_name={property_name!r}."
        )
    if len(matches) > 1:
        names = ", ".join(table.name for table in matches)
        raise ValueError(f"Result table selector matched multiple tables: {names}")
    return matches[0]


def read_solution_result(
    connection: duckdb.DuckDBPyConnection,
    table: ResultTable | str,
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
    if isinstance(table, ResultTable):
        table_name = table.name
        schema = table.schema
    else:
        table_name = table
        schema = "report"

    available_columns = table_columns(connection, table_name, schema=schema)
    selected_columns = normalize_columns(columns)
    select_sql = "*" if selected_columns is None else quote_column_list(selected_columns, available_columns)

    conditions: list[str] = []
    params: list[Any] = []
    add_in_filter(
        conditions,
        params,
        column="name",
        values=normalize_optional_names(object_names),
        available_columns=available_columns,
        filter_name="object_names",
    )
    if category is not None:
        add_equals_filter(
            conditions,
            params,
            column="category",
            value=category,
            available_columns=available_columns,
            filter_name="category",
        )
    add_in_filter(
        conditions,
        params,
        column="sample_name",
        values=normalize_optional_names(sample_names),
        available_columns=available_columns,
        filter_name="sample_names",
    )
    band_column = first_present_column(available_columns, ("band", "band_id"))
    if bands is not None:
        if band_column is None:
            raise ValueError(f"Cannot filter by bands; {schema}.{table_name} has no band column.")
        add_in_filter(
            conditions,
            params,
            column=band_column,
            values=normalize_bands(bands),
            available_columns=available_columns,
            filter_name="bands",
        )
    timestamp_column = first_present_column(available_columns, ("timestamp", "datetime"))
    if start is not None:
        if timestamp_column is None:
            raise ValueError(f"Cannot filter by start; {schema}.{table_name} has no timestamp column.")
        conditions.append(f"{quote_identifier(timestamp_column)} >= ?")
        params.append(start)
    if end is not None:
        if timestamp_column is None:
            raise ValueError(f"Cannot filter by end; {schema}.{table_name} has no timestamp column.")
        conditions.append(f"{quote_identifier(timestamp_column)} < ?")
        params.append(end)

    where_sql = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT {select_sql} FROM {quote_qualified_table(schema, table_name)}{where_sql}"
    return connection.sql(sql, params=params or None)


def parse_result_table_name(
    table_name: str,
    *,
    schema: ResultSchema,
    table_type: str,
    property_map: dict[tuple[str, str], str],
) -> ResultTable | None:
    """Parse a plexos2duckdb result table name into a ResultTable model."""
    parts = table_name.split("__", 3)
    if len(parts) != 4:
        return None
    phase_label, period_label, collection_label, property_label = parts
    phase = parse_result_phase(phase_label)
    period = parse_result_period(period_label)
    collection = parse_collection_label(collection_label)
    parsed_table_type = parse_table_type(table_type)
    if phase is None or period is None or collection is None or parsed_table_type is None:
        return None
    property_name = property_map.get((collection.value, property_label), property_label)
    return ResultTable(
        name=table_name,
        schema=schema,
        phase=phase,
        period=period,
        class_enum=class_for_collection(collection),
        collection=collection,
        property_name=property_name,
        table_type=parsed_table_type,
        value_column="value" if schema == "data" else property_label,
    )


def result_property_name_map(connection: duckdb.DuckDBPyConnection) -> dict[tuple[str, str], str]:
    """Map (collection, result-table property label) to the PLEXOS property name."""
    try:
        rows = connection.execute(
            """
            SELECT DISTINCT collection, property
            FROM processed.properties
            WHERE collection IS NOT NULL AND property IS NOT NULL
            """
        ).fetchall()
    except duckdb.Error:
        return {}
    return {(str(collection), table_label(str(prop))): str(prop) for collection, prop in rows}


def table_columns(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    *,
    schema: DuckDBSchema,
) -> set[str]:
    """Return column names for one DuckDB table or view."""
    rows = connection.execute(f"DESCRIBE {quote_qualified_table(schema, table_name)}").fetchall()
    return {str(row[0]) for row in rows}


def validate_read_query(query_string: str) -> None:
    """Reject write statements passed through read-oriented query helpers."""
    first_word = query_string.strip().split(maxsplit=1)[0].upper() if query_string.strip() else ""
    if first_word not in ("SELECT", "WITH", "DESCRIBE", "SHOW", "EXPLAIN"):
        raise ValueError("query() and query_dicts() only accept read-only queries.")


def validate_result_schema(schema: str) -> None:
    """Validate a result schema name."""
    if schema not in ("data", "report"):
        raise ValueError("schema must be 'data' or 'report'")


def quote_identifier(identifier: str) -> str:
    """Quote one DuckDB identifier."""
    return '"' + identifier.replace('"', '""') + '"'


def quote_qualified_table(schema: str, table_name: str) -> str:
    """Quote a schema-qualified DuckDB table name."""
    return f"{quote_identifier(schema)}.{quote_identifier(table_name)}"


def quote_column_list(columns: Sequence[str], available_columns: set[str]) -> str:
    """Quote a selected column list after validating column names."""
    missing = [column for column in columns if column not in available_columns]
    if missing:
        raise KeyError(f"Columns not found: {missing}")
    return ", ".join(quote_identifier(column) for column in columns)


def normalize_columns(columns: Sequence[str] | None) -> list[str] | None:
    """Normalize a column sequence while treating a bare string as one column."""
    if columns is None:
        return None
    if isinstance(columns, str):
        return [columns]
    return list(columns)


def normalize_optional_names(values: str | Iterable[str] | None) -> list[str] | None:
    """Normalize optional single-or-many string filters."""
    if values is None:
        return None
    return normalize_names(values)


def normalize_bands(values: int | Iterable[int]) -> list[int]:
    """Normalize optional single-or-many band filters."""
    if isinstance(values, int):
        return [values]
    return [int(value) for value in values]


def add_in_filter(
    conditions: list[str],
    params: list[Any],
    *,
    column: str,
    values: Sequence[Any] | None,
    available_columns: set[str],
    filter_name: str,
) -> None:
    """Append an IN filter when values are provided."""
    if values is None:
        return
    if column not in available_columns:
        raise ValueError(f"Cannot filter by {filter_name}; column {column!r} is not present.")
    if not values:
        conditions.append("FALSE")
        return
    placeholders = ", ".join("?" for _ in values)
    conditions.append(f"{quote_identifier(column)} IN ({placeholders})")
    params.extend(values)


def add_equals_filter(
    conditions: list[str],
    params: list[Any],
    *,
    column: str,
    value: Any,
    available_columns: set[str],
    filter_name: str,
) -> None:
    """Append an equality filter."""
    if column not in available_columns:
        raise ValueError(f"Cannot filter by {filter_name}; column {column!r} is not present.")
    conditions.append(f"{quote_identifier(column)} = ?")
    params.append(value)


def first_present_column(available_columns: set[str], candidates: Sequence[str]) -> str | None:
    """Return the first candidate present in a column set."""
    return next((candidate for candidate in candidates if candidate in available_columns), None)


def table_label(value: str) -> str:
    """Return the label form used inside plexos2duckdb result table names."""
    return value.strip().replace(" ", "_").replace("-", "_")


def normalize_collection(value: CollectionEnum | str) -> CollectionEnum:
    """Normalize a public collection argument to a collection enum."""
    if isinstance(value, CollectionEnum):
        return value
    collection = parse_collection_label(value)
    if collection is None:
        raise ValueError(f"{value!r} is not a valid CollectionEnum")
    return collection


def parse_collection_label(label: str) -> CollectionEnum | None:
    """Parse a collection label from a public value or result table name."""
    for candidate in (label, label.replace("_", " ")):
        try:
            return parse_collection_enum(candidate)
        except ValueError:
            continue
    return None


def collection_matches(left: CollectionEnum, right: CollectionEnum) -> bool:
    """Return True when two collection values identify the same collection."""
    return left == right


def class_for_collection(collection: CollectionEnum) -> ClassEnum | None:
    """Infer the default PLEXOS class represented by a result collection."""
    for class_enum in ClassEnum:
        try:
            default_collection = get_default_collection(class_enum)
        except KeyError:
            continue
        if default_collection == collection:
            return class_enum
    return None


def normalize_result_phase(value: ResultPhase | str) -> ResultPhase:
    """Normalize a public result phase argument to ResultPhase."""
    if isinstance(value, ResultPhase):
        return value
    parsed = parse_result_phase(value)
    if parsed is None:
        raise ValueError(f"{value!r} is not a valid ResultPhase")
    return parsed


def normalize_result_period(value: ResultPeriod | str) -> ResultPeriod:
    """Normalize a public result period argument to ResultPeriod."""
    if isinstance(value, ResultPeriod):
        return value
    parsed = parse_result_period(value)
    if parsed is None:
        raise ValueError(f"{value!r} is not a valid ResultPeriod")
    return parsed


def parse_result_phase(value: str) -> ResultPhase | None:
    """Parse a result phase after runtime validation."""
    try:
        return ResultPhase(value.upper())
    except ValueError:
        return None


def parse_result_period(value: str) -> ResultPeriod | None:
    """Parse a result period after runtime validation."""
    try:
        return ResultPeriod(value.upper())
    except ValueError:
        return None


def parse_table_type(value: str) -> TableType | None:
    """Parse a DuckDB information_schema table type after runtime validation."""
    try:
        return TableType(value.upper())
    except ValueError:
        return None
