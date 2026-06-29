from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest

from plexosdb import DuckDBResult
from plexosdb import DuckDBSolutionInfo as ExportedDuckDBSolutionInfo
from plexosdb import PlexosSolution as ExportedPlexosSolution
from plexosdb import ResultTable as ExportedResultTable
from plexosdb.db_solution import PlexosSolution
from plexosdb.db_solution_models import DuckDBSolutionInfo, ResultTable
from plexosdb.enums import ClassEnum, CollectionEnum


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
