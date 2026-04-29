"""Tests for PlexosDB.iterate_properties() method."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from plexosdb import PlexosDB


def test_iterate_properties_with_class_enum_only(db_with_topology: PlexosDB) -> None:
    from plexosdb import ClassEnum

    results = list(db_with_topology.iterate_properties(class_enum=ClassEnum.Generator))

    assert isinstance(results, list)


def test_iterate_properties_with_parent_class_only(db_with_topology: PlexosDB) -> None:
    from plexosdb import ClassEnum

    results = list(db_with_topology.iterate_properties(parent_class=ClassEnum.System))

    assert isinstance(results, list)


def test_iterate_properties_with_collection_validation(db_with_topology: PlexosDB) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    results = list(
        db_with_topology.iterate_properties(
            class_enum=ClassEnum.Generator,
            parent_class=ClassEnum.System,
            collection=CollectionEnum.Generators,
        )
    )

    assert isinstance(results, list)


def test_iterate_properties_with_object_names_validation(db_thermal_gen: PlexosDB) -> None:
    from plexosdb import ClassEnum

    results = list(
        db_thermal_gen.iterate_properties(
            class_enum=ClassEnum.Generator,
            object_names="thermal-01",
        )
    )

    assert isinstance(results, list)


def test_iterate_properties_with_property_names_and_collection_class(
    db_thermal_gen: PlexosDB,
) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    results = list(
        db_thermal_gen.iterate_properties(
            class_enum=ClassEnum.Generator,
            property_names="Max Capacity",
            collection=CollectionEnum.Generators,
        )
    )

    assert isinstance(results, list)


def test_iterate_properties_with_property_names_no_collection(db_thermal_gen: PlexosDB) -> None:
    results = list(
        db_thermal_gen.iterate_properties(
            property_names="Max Capacity",
        )
    )

    assert isinstance(results, list)


def test_iterate_properties_with_category_check(db_with_topology: PlexosDB) -> None:
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NotFoundError

    with pytest.raises(NotFoundError, match="Category 'nonexistent' does not exist"):
        list(
            db_with_topology.iterate_properties(
                class_enum=ClassEnum.Generator,
                category="nonexistent",
            )
        )


def test_iterate_properties_yields_property_records(db_thermal_gen: PlexosDB) -> None:
    from plexosdb import ClassEnum

    results = list(
        db_thermal_gen.iterate_properties(
            class_enum=ClassEnum.Generator,
            object_names="thermal-01",
        )
    )

    assert len(results) > 0
    for record in results:
        assert isinstance(record, dict)


def test_iterate_properties_with_non_system_parent_class(
    db_with_reserve_collection_property: PlexosDB,
) -> None:
    """Test that parent_class context is propagated for property validation."""
    from plexosdb import ClassEnum, CollectionEnum

    db = db_with_reserve_collection_property

    results = list(
        db.iterate_properties(
            class_enum=ClassEnum.Region,
            object_names="region-01",
            property_names=["Load Risk"],
            parent_class=ClassEnum.Reserve,
            collection=CollectionEnum.Regions,
        )
    )

    assert len(results) == 1
    assert results[0]["property"] == "Load Risk"


def test_get_object_properties_with_non_system_parent_class(
    db_with_reserve_collection_property: PlexosDB,
) -> None:
    """Test that get_object_properties respects parent_class_enum for validation."""
    from plexosdb import ClassEnum, CollectionEnum

    db = db_with_reserve_collection_property

    props = db.get_object_properties(
        ClassEnum.Region,
        "region-01",
        property_names=["Load Risk"],
        parent_class_enum=ClassEnum.Reserve,
        collection_enum=CollectionEnum.Regions,
    )

    assert len(props) == 1
    assert props[0]["property"] == "Load Risk"


def _setup_scenario_tagged_generator_properties(db: PlexosDB) -> None:
    from plexosdb import ClassEnum

    db.add_scenario("ScenarioA", category="CatA")
    db.add_scenario("ScenarioB", category="CatB")
    db.add_scenario("ScenarioC", category="CatA")

    db.add_property(ClassEnum.Generator, "thermal-01", "Heat Rate", 10.0, band=1, scenario="ScenarioA")
    db.add_property(ClassEnum.Generator, "thermal-01", "Heat Rate", 11.0, band=2, scenario="ScenarioB")
    db.add_property(ClassEnum.Generator, "thermal-01", "Heat Rate", 12.0, band=3, scenario="ScenarioC")


def test_iterate_properties_filters_by_scenario(db_with_topology: PlexosDB) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    db = db_with_topology
    _setup_scenario_tagged_generator_properties(db)
    results = list(
        db.iterate_properties(
            class_enum=ClassEnum.Generator,
            object_names="thermal-01",
            property_names="Heat Rate",
            collection=CollectionEnum.Generators,
            scenario="ScenarioB",
        )
    )

    assert len(results) == 1
    assert results[0]["scenario_name"] == "ScenarioB"


def test_iterate_properties_filters_by_scenario_category(db_with_topology: PlexosDB) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    db = db_with_topology
    _setup_scenario_tagged_generator_properties(db)
    results = list(
        db.iterate_properties(
            class_enum=ClassEnum.Generator,
            object_names="thermal-01",
            property_names="Heat Rate",
            collection=CollectionEnum.Generators,
            scenario_category="CatA",
        )
    )

    assert len(results) == 2
    assert {row["scenario_name"] for row in results} == {"ScenarioA", "ScenarioC"}


def test_get_object_properties_filters_by_scenario(db_with_topology: PlexosDB) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    db = db_with_topology
    _setup_scenario_tagged_generator_properties(db)
    props = db.get_object_properties(
        ClassEnum.Generator,
        "thermal-01",
        property_names="Heat Rate",
        collection_enum=CollectionEnum.Generators,
        scenario="ScenarioA",
    )

    assert len(props) == 1
    assert props[0]["scenario_name"] == "ScenarioA"


def test_get_object_properties_filters_by_scenario_and_category(
    db_with_topology: PlexosDB,
) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    db = db_with_topology
    _setup_scenario_tagged_generator_properties(db)
    props = db.get_object_properties(
        ClassEnum.Generator,
        "thermal-01",
        property_names="Heat Rate",
        collection_enum=CollectionEnum.Generators,
        scenario="ScenarioC",
        scenario_category="CatA",
    )

    assert len(props) == 1
    assert props[0]["scenario_name"] == "ScenarioC"
