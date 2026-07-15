from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import duckdb
import pytest

from plexosdb import DuckDBResult
from plexosdb import DuckDBSolutionInfo as ExportedDuckDBSolutionInfo
from plexosdb import PlexosSolution as ExportedPlexosSolution
from plexosdb import ResultTable as ExportedResultTable
from plexosdb.db_solution import PlexosSolution
from plexosdb.db_solution_helpers import (
    add_equals_filter,
    add_in_filter,
    convert_solution_to_duckdb,
    copy_duckdb_to_memory,
    normalize_bands,
    normalize_collection,
    normalize_columns,
    normalize_optional_names,
    normalize_result_period,
    normalize_result_phase,
    parse_collection_label,
    parse_result_period,
    parse_result_phase,
    parse_result_table_name,
    parse_table_type,
    read_solution_result,
    solution_metadata_source,
    solution_metadata_value,
    validate_read_query,
    validate_result_schema,
)
from plexosdb.db_solution_models import DuckDBSolutionInfo, ResultTable
from plexosdb.enums import ClassEnum, CollectionEnum, PeriodEnum, PhaseEnum


@pytest.fixture(scope="module")
def solution_duckdb(
    tmp_path_factory: pytest.TempPathFactory,
    solution_zip: Path,
) -> Generator[PlexosSolution]:
    """DuckDB solution with one generated result table for focused API tests."""
    db_path = tmp_path_factory.mktemp("duckdb_solution") / "solution.duckdb"
    sol = PlexosSolution.from_zip(solution_zip)
    sol.to_duckdb(
        db_path,
        if_exists="replace",
        in_memory=False,
        table_name_pattern="ST__Interval__Generators__Generation",
    )
    try:
        yield sol
    finally:
        sol.close()


def test_top_level_exports_use_duckdb_solution_api():
    assert ExportedPlexosSolution is PlexosSolution
    assert ExportedDuckDBSolutionInfo is DuckDBSolutionInfo
    assert ExportedResultTable is ResultTable
    assert DuckDBResult.__module__ == "plexosdb.db_solution_models"


def test_plexos_solution_direct_constructor_is_not_public(solution_zip: Path):
    with pytest.raises(TypeError, match="from_zip"):
        PlexosSolution()
    with pytest.raises(TypeError, match="from_zip"):
        PlexosSolution(solution_zip)  # type: ignore[call-arg]


def test_solution_info_and_query_primitives(solution_duckdb: PlexosSolution, solution_zip: Path):
    info = solution_duckdb.info()
    assert isinstance(info, DuckDBSolutionInfo)
    assert info.source == solution_zip
    assert info.database is not None
    assert info.model_name == "Base + Run of River"
    assert info.converter_version

    assert solution_duckdb.query("SELECT COUNT(*) FROM processed.objects")[0][0] > 0
    rows = solution_duckdb.query_dicts(
        "SELECT name FROM processed.objects WHERE name = ?",
        ("Coal_Gen",),
    )
    assert rows == [{"name": "Coal_Gen"}]
    assert solution_duckdb.sql("SELECT COUNT(*) AS n FROM processed.objects").fetchone()[0] > 0
    assert solution_duckdb.table("ST__Interval__Generators__Generation").limit(1).fetchone() is not None


def test_solution_metadata_discovery_uses_existing_enums(solution_duckdb: PlexosSolution):
    objects = solution_duckdb.list_objects_by_class(ClassEnum.Generator)
    assert "Coal_Gen" in objects
    assert objects == solution_duckdb.list_objects_by_class("Generator")

    table = solution_duckdb.result_table(
        class_enum=ClassEnum.Generator,
        property_name="Generation",
    )
    assert isinstance(table, ResultTable)
    assert table.collection == CollectionEnum.Generators
    assert table.class_enum == ClassEnum.Generator
    assert table.value_column == "Generation"

    tables = solution_duckdb.list_result_tables(
        collection=CollectionEnum.Generators,
        property_name="Generation",
    )
    assert tables == [table]


def test_read_result_returns_filtered_duckdb_relation(solution_duckdb: PlexosSolution):
    table = solution_duckdb.result_table(
        class_enum=ClassEnum.Generator,
        property_name="Generation",
    )
    relation = solution_duckdb.get_result(
        table,
        object_names="Coal_Gen",
        columns=["name", "timestamp", "Generation"],
    )
    rows = relation.fetchall()
    assert len(rows) == 8760
    assert rows[0][0] == "Coal_Gen"

    one_day = solution_duckdb.get_result(
        "ST__Interval__Generators__Generation",
        object_names=["Coal_Gen"],
        start="2017-01-01",
        end="2017-01-02",
    )
    assert len(one_day.fetchall()) == 24


def test_read_result_rejects_missing_filter_columns(solution_duckdb: PlexosSolution):
    data_table = solution_duckdb.result_table(
        schema="data",
        class_enum=ClassEnum.Generator,
        property_name="Generation",
    )
    with pytest.raises(ValueError, match="object_names"):
        solution_duckdb.get_result(data_table, object_names="Coal_Gen")


# ---------------------------------------------------------------------------
# PlexosSolution construction / lifecycle
# ---------------------------------------------------------------------------


def test_from_zip_nonexistent_path():
    with pytest.raises(FileNotFoundError):
        PlexosSolution.from_zip("/no/such/file.zip")


def test_to_duckdb_invalid_if_exists(solution_zip: Path):
    sol = PlexosSolution.from_zip(solution_zip)
    with pytest.raises(ValueError, match="if_exists"):
        sol.to_duckdb(if_exists="invalid")  # type: ignore[arg-type]


def test_list_tables_default_schema(solution_duckdb: PlexosSolution):
    tables = solution_duckdb.list_tables()
    names = [t.name for t in tables]
    assert "ST__Interval__Generators__Generation" in names


def test_list_tables_raw_schema(solution_duckdb: PlexosSolution):
    tables = solution_duckdb.list_tables(schema="raw")
    assert len(tables) > 0


def test_context_manager_closes_connection(solution_zip: Path, tmp_path: Path):
    db_path = tmp_path / "ctx.duckdb"
    sol = PlexosSolution.from_zip(solution_zip)
    sol.to_duckdb(db_path, if_exists="replace", table_name_pattern="ST__Interval__Generators__Generation")
    with sol:
        assert sol.query("SELECT COUNT(*) FROM processed.objects")[0][0] > 0
    with pytest.raises(RuntimeError, match="No active connection"):
        _ = sol.connection


def test_connection_property_raises_when_no_connection(solution_zip: Path):
    sol = PlexosSolution.from_zip(solution_zip)
    with pytest.raises(RuntimeError, match="No active connection"):
        _ = sol.connection


def test_to_duckdb_in_memory(solution_zip: Path):
    sol = PlexosSolution.from_zip(solution_zip)
    result = sol.to_duckdb(table_name_pattern="ST__Interval__Generators__Generation")
    try:
        assert result.is_in_memory
        assert sol.query("SELECT COUNT(*) FROM processed.objects")[0][0] > 0
    finally:
        sol.close()


# ---------------------------------------------------------------------------
# convert_solution_to_duckdb / copy_duckdb_to_memory
# ---------------------------------------------------------------------------


def test_convert_solution_to_duckdb_fail_raises(tmp_path: Path):
    db_path = tmp_path / "existing.duckdb"
    db_path.touch()
    with pytest.raises(FileExistsError):
        convert_solution_to_duckdb(
            Path("dummy.zip"), db_path, if_exists="fail", n_threads=None, table_name_pattern=None
        )


def test_convert_solution_to_duckdb_reuse_returns_existing(tmp_path: Path):
    db_path = tmp_path / "existing.duckdb"
    db_path.touch()
    result = convert_solution_to_duckdb(
        Path("dummy.zip"), db_path, if_exists="reuse", n_threads=None, table_name_pattern=None
    )
    assert result == db_path


def test_copy_duckdb_to_memory(solution_duckdb: PlexosSolution):
    db_path = solution_duckdb._database_path
    assert db_path is not None
    conn = copy_duckdb_to_memory(db_path)
    try:
        count = conn.execute("SELECT COUNT(*) FROM processed.objects").fetchone()
        assert count is not None and count[0] > 0
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# solution_metadata helpers
# ---------------------------------------------------------------------------


def test_solution_metadata_value_none_connection():
    assert solution_metadata_value(None, "any_key") is None


def test_solution_metadata_value_missing_table():
    conn = duckdb.connect(":memory:")
    assert solution_metadata_value(conn, "any_key") is None
    conn.close()


def test_solution_metadata_value_null_value():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE main.plexos2duckdb (key VARCHAR, value VARCHAR)")
    conn.execute("INSERT INTO main.plexos2duckdb VALUES ('k', NULL)")
    assert solution_metadata_value(conn, "k") is None
    conn.close()


def test_solution_metadata_source_returns_path():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE main.plexos2duckdb (key VARCHAR, value VARCHAR)")
    conn.execute("INSERT INTO main.plexos2duckdb VALUES ('plexos_file', '/path/to/model.zip')")
    result = solution_metadata_source(conn)
    assert result == Path("/path/to/model.zip")
    conn.close()


def test_solution_metadata_source_returns_none_when_empty():
    conn = duckdb.connect(":memory:")
    assert solution_metadata_source(conn) is None
    conn.close()


# ---------------------------------------------------------------------------
# table() with ResultTable object
# ---------------------------------------------------------------------------


def test_table_method_with_result_table_object(solution_duckdb: PlexosSolution):
    rt = solution_duckdb.result_table(class_enum=ClassEnum.Generator, property_name="Generation")
    relation = solution_duckdb.table(rt)
    assert relation.limit(1).fetchone() is not None


# ---------------------------------------------------------------------------
# list_objects_by_class with category
# ---------------------------------------------------------------------------


def test_list_objects_by_class_with_category(solution_duckdb: PlexosSolution):
    objects = solution_duckdb.list_objects_by_class(ClassEnum.Generator, category="Thermal")
    assert isinstance(objects, list)


# ---------------------------------------------------------------------------
# list_result_tables filter "continue" paths (non-matching filters)
# ---------------------------------------------------------------------------


def test_list_result_tables_phase_filter_no_match(solution_duckdb: PlexosSolution):
    assert solution_duckdb.list_result_tables(phase=PhaseEnum.LT) == []


def test_list_result_tables_period_filter_no_match(solution_duckdb: PlexosSolution):
    assert solution_duckdb.list_result_tables(period=PeriodEnum.YEAR) == []


def test_list_result_tables_collection_filter_no_match(solution_duckdb: PlexosSolution):
    assert solution_duckdb.list_result_tables(collection=CollectionEnum.Fuels) == []


def test_list_result_tables_class_filter_no_match(solution_duckdb: PlexosSolution):
    assert solution_duckdb.list_result_tables(class_enum=ClassEnum.Fuel) == []


def test_list_result_tables_property_name_filter_no_match(solution_duckdb: PlexosSolution):
    assert solution_duckdb.list_result_tables(property_name="NoSuchProperty") == []


# ---------------------------------------------------------------------------
# result_table error paths
# ---------------------------------------------------------------------------


def test_result_table_no_match_raises_key_error(solution_duckdb: PlexosSolution):
    with pytest.raises(KeyError, match="No result table matched"):
        solution_duckdb.result_table(property_name="NoSuchProperty")


def test_result_table_multiple_matches_raises_value_error(solution_duckdb: PlexosSolution):
    rt = solution_duckdb.result_table(class_enum=ClassEnum.Generator, property_name="Generation")
    with patch(
        "plexosdb.db_solution_helpers.list_solution_result_tables",
        return_value=[rt, rt],
    ):
        with pytest.raises(ValueError, match="matched multiple tables"):
            solution_duckdb.result_table(property_name="Generation")


# ---------------------------------------------------------------------------
# get_result with various filters
# ---------------------------------------------------------------------------


def test_get_result_with_category_filter(solution_duckdb: PlexosSolution):
    relation = solution_duckdb.get_result(
        "ST__Interval__Generators__Generation",
        category="Thermal",
    )
    assert relation is not None


def test_get_result_with_bands_filter(solution_duckdb: PlexosSolution):
    relation = solution_duckdb.get_result(
        "ST__Interval__Generators__Generation",
        object_names="Coal_Gen",
        bands=1,
    )
    assert relation is not None


def test_get_result_column_as_string(solution_duckdb: PlexosSolution):
    relation = solution_duckdb.get_result(
        "ST__Interval__Generators__Generation",
        columns="name",
    )
    row = relation.limit(1).fetchone()
    assert row is not None


def test_get_result_start_end_filter(solution_duckdb: PlexosSolution):
    relation = solution_duckdb.get_result(
        "ST__Interval__Generators__Generation",
        object_names="Coal_Gen",
        start="2017-06-01",
        end="2017-06-02",
    )
    assert len(relation.fetchall()) == 24


# ---------------------------------------------------------------------------
# read_solution_result error paths (no timestamp / no band column)
# ---------------------------------------------------------------------------


def _make_simple_conn(columns: str) -> duckdb.DuckDBPyConnection:
    """Return an in-memory DuckDB connection with a single-row report.t table."""
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE SCHEMA report")
    conn.execute(f"CREATE TABLE report.t ({columns})")
    conn.execute(f"INSERT INTO report.t VALUES ({', '.join(['1'] * columns.count(',') + ['1'])})")
    return conn


def test_read_solution_result_start_no_timestamp_raises():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE SCHEMA report")
    conn.execute("CREATE TABLE report.t (name VARCHAR, value DOUBLE)")
    conn.execute("INSERT INTO report.t VALUES ('a', 1.0)")
    with pytest.raises(ValueError, match="start"):
        read_solution_result(conn, "t", sample_names=None, start="2017-01-01")
    conn.close()


def test_read_solution_result_end_no_timestamp_raises():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE SCHEMA report")
    conn.execute("CREATE TABLE report.t (name VARCHAR, value DOUBLE)")
    conn.execute("INSERT INTO report.t VALUES ('a', 1.0)")
    with pytest.raises(ValueError, match="end"):
        read_solution_result(conn, "t", sample_names=None, end="2017-01-02")
    conn.close()


def test_read_solution_result_bands_no_band_column_raises():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE SCHEMA report")
    conn.execute("CREATE TABLE report.t (name VARCHAR, value DOUBLE)")
    conn.execute("INSERT INTO report.t VALUES ('a', 1.0)")
    with pytest.raises(ValueError, match="band"):
        read_solution_result(conn, "t", sample_names=None, bands=1)
    conn.close()


def test_parse_result_table_name_too_few_parts():
    assert (
        parse_result_table_name("only__three", schema="report", table_type="BASE TABLE", property_map={})
        is None
    )


def test_parse_result_table_name_bad_phase():
    result = parse_result_table_name(
        "BADPHASE__Interval__Generators__Generation",
        schema="report",
        table_type="BASE TABLE",
        property_map={},
    )
    assert result is None


def test_parse_result_table_name_bad_period():
    result = parse_result_table_name(
        "ST__BADPERIOD__Generators__Generation",
        schema="report",
        table_type="BASE TABLE",
        property_map={},
    )
    assert result is None


def test_parse_result_table_name_bad_collection():
    result = parse_result_table_name(
        "ST__Interval__UnknownCollection__Generation",
        schema="report",
        table_type="BASE TABLE",
        property_map={},
    )
    assert result is None


def test_parse_result_table_name_bad_table_type():
    result = parse_result_table_name(
        "ST__Interval__Generators__Generation",
        schema="report",
        table_type="UNKNOWN_TYPE",
        property_map={},
    )
    assert result is None


def test_parse_result_table_name_data_schema_value_column():
    result = parse_result_table_name(
        "ST__Interval__Generators__Generation",
        schema="data",
        table_type="BASE TABLE",
        property_map={},
    )
    assert result is not None
    assert result.value_column == "value"


# ---------------------------------------------------------------------------
# Pure utility helpers
# ---------------------------------------------------------------------------


def test_validate_read_query_rejects_write():
    with pytest.raises(ValueError, match="read-only"):
        validate_read_query("INSERT INTO foo VALUES (1)")
    with pytest.raises(ValueError, match="read-only"):
        validate_read_query("UPDATE foo SET x = 1")
    with pytest.raises(ValueError, match="read-only"):
        validate_read_query("DELETE FROM foo")
    # These should not raise
    validate_read_query("SELECT 1")
    validate_read_query("WITH cte AS (SELECT 1) SELECT * FROM cte")


def test_validate_result_schema_invalid():
    with pytest.raises(ValueError, match="schema must be"):
        validate_result_schema("raw")
    with pytest.raises(ValueError, match="schema must be"):
        validate_result_schema("processed")


def test_normalize_columns_string_input():
    assert normalize_columns("name") == ["name"]


def test_normalize_columns_none():
    assert normalize_columns(None) is None


def test_normalize_columns_list():
    assert normalize_columns(["a", "b"]) == ["a", "b"]


def test_normalize_bands_single_int():
    assert normalize_bands(3) == [3]


def test_normalize_bands_list():
    assert normalize_bands([1, 2]) == [1, 2]


def test_normalize_optional_names_none():
    assert normalize_optional_names(None) is None


def test_normalize_optional_names_string():
    assert normalize_optional_names("Coal_Gen") == ["Coal_Gen"]


def test_add_in_filter_empty_values_appends_false():
    conditions: list[str] = []
    params: list = []
    add_in_filter(
        conditions, params, column="name", values=[], available_columns={"name"}, filter_name="test"
    )
    assert conditions == ["FALSE"]
    assert params == []


def test_add_in_filter_missing_column_raises():
    with pytest.raises(ValueError, match="test_filter"):
        add_in_filter(
            [], [], column="missing", values=["x"], available_columns={"name"}, filter_name="test_filter"
        )


def test_add_equals_filter_missing_column_raises():
    with pytest.raises(ValueError, match="category"):
        add_equals_filter(
            [], [], column="category", value="x", available_columns={"name"}, filter_name="category"
        )


def test_normalize_collection_invalid_raises():
    with pytest.raises(ValueError):
        normalize_collection("NotAValidCollection")


def test_parse_collection_label_unknown_returns_none():
    assert parse_collection_label("XyzUnknownCollection") is None


def test_normalize_result_phase_invalid_raises():
    with pytest.raises(ValueError):
        normalize_result_phase("INVALID_PHASE")


def test_normalize_result_period_invalid_raises():
    with pytest.raises(ValueError):
        normalize_result_period("INVALID_PERIOD")


def test_parse_result_phase_invalid_returns_none():
    assert parse_result_phase("BADPHASE") is None


def test_parse_result_period_invalid_returns_none():
    assert parse_result_period("BADPERIOD") is None


def test_parse_table_type_invalid_returns_none():
    assert parse_table_type("UNKNOWN_TABLE_TYPE") is None
