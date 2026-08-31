from pathlib import Path

import pytest

from plexosdb import ClassEnum, CollectionEnum, PlexosDB
from plexosdb.exceptions import NameError, NotFoundError


XML_PATH = Path(__file__).parent / "data" / "run_of_river_case" / "TestSystem.xml"


@pytest.fixture
def run_of_river_db():
    db = PlexosDB.from_xml(XML_PATH)
    yield db
    db._db.close()


def _property_rows(db: PlexosDB, object_name: str, property_name: str) -> list[tuple]:
    properties = db.get_object_properties(ClassEnum.Generator, object_name, property_names=property_name)
    return sorted((property["value"], property.get("band") or 1) for property in properties)


def test_update_property_updates_xml_fixture_value(run_of_river_db: PlexosDB) -> None:
    run_of_river_db.update_property(
        "Coal_Gen",
        "Max Capacity",
        625.0,
        object_class=ClassEnum.Generator,
    )

    rows = _property_rows(run_of_river_db, "Coal_Gen", "Max Capacity")
    assert rows == [(625.0, 1)]


def test_update_property_only_updates_requested_band(run_of_river_db: PlexosDB) -> None:
    run_of_river_db.update_property(
        "Gas_Gen2",
        "Load Point",
        95.0,
        object_class=ClassEnum.Generator,
        band=2,
    )

    rows = _property_rows(run_of_river_db, "Gas_Gen2", "Load Point")
    assert rows == [(95.0 if band == 2 else 50.0 + 20.0 * band, band) for band in range(1, 11)]


def test_band_one_matches_unbanded_property_for_single_and_bulk_updates(run_of_river_db: PlexosDB) -> None:
    run_of_river_db.update_property(
        "Coal_Gen",
        "Max Capacity",
        625.0,
        object_class=ClassEnum.Generator,
        band=1,
    )
    assert _property_rows(run_of_river_db, "Coal_Gen", "Max Capacity") == [(625.0, 1)]

    run_of_river_db.update_properties(
        [
            {
                "object_name": "Gas_Gen1",
                "property_name": "Max Capacity",
                "new_value": 325.0,
                "object_class": ClassEnum.Generator,
                "band": 1,
            }
        ]
    )
    assert _property_rows(run_of_river_db, "Gas_Gen1", "Max Capacity") == [(325.0, 1)]


def test_update_properties_updates_multiple_xml_fixture_values(run_of_river_db: PlexosDB) -> None:
    run_of_river_db.update_properties(
        [
            {
                "object_name": "Coal_Gen",
                "property_name": "Max Capacity",
                "new_value": 625.0,
                "object_class": ClassEnum.Generator,
            },
            {
                "object_name": "Gas_Gen1",
                "property_name": "Max Capacity",
                "new_value": 325.0,
                "object_class": ClassEnum.Generator,
            },
        ]
    )

    assert _property_rows(run_of_river_db, "Coal_Gen", "Max Capacity") == [(625.0, 1)]
    assert _property_rows(run_of_river_db, "Gas_Gen1", "Max Capacity") == [(325.0, 1)]


def test_update_properties_rejects_missing_scenario(run_of_river_db: PlexosDB) -> None:
    with pytest.raises(NotFoundError, match="Missing Scenario"):
        run_of_river_db.update_properties(
            [
                {
                    "object_name": "Coal_Gen",
                    "property_name": "Max Capacity",
                    "new_value": 625.0,
                    "object_class": ClassEnum.Generator,
                    "scenario": "Missing Scenario",
                }
            ]
        )


def test_update_properties_chunks_large_object_validation(db_base: PlexosDB) -> None:
    object_names = [f"Generator{i}" for i in range(1000)]
    db_base.add_objects(ClassEnum.Generator, *object_names)
    db_base.add_properties_from_records(
        [{"name": name, "property": "Max Capacity", "value": 100.0} for name in object_names],
        object_class=ClassEnum.Generator,
        collection=CollectionEnum.Generators,
        scenario="Base Case",
    )

    db_base.update_properties(
        [
            {
                "object_name": name,
                "property_name": "Max Capacity",
                "new_value": 200.0,
                "object_class": ClassEnum.Generator,
                "scenario": "Base Case",
            }
            for name in object_names
        ]
    )

    assert _property_rows(db_base, "Generator999", "Max Capacity") == [(200.0, 1)]


def test_update_properties_rolls_back_domain_validation_failure_and_reuses_connection(
    run_of_river_db: PlexosDB,
) -> None:
    original_rows = _property_rows(run_of_river_db, "Coal_Gen", "Max Capacity")

    with pytest.raises(NameError):
        run_of_river_db.update_properties(
            [
                {
                    "object_name": "Coal_Gen",
                    "property_name": "Max Capacity",
                    "new_value": 625.0,
                    "object_class": ClassEnum.Generator,
                },
                {
                    "object_name": "Coal_Gen",
                    "property_name": "Not a property",
                    "new_value": 1.0,
                    "object_class": ClassEnum.Generator,
                },
            ]
        )

    assert _property_rows(run_of_river_db, "Coal_Gen", "Max Capacity") == original_rows

    run_of_river_db.update_property(
        "Coal_Gen",
        "Max Capacity",
        625.0,
        object_class=ClassEnum.Generator,
    )
    assert _property_rows(run_of_river_db, "Coal_Gen", "Max Capacity") == [(625.0, 1)]


def test_update_property_uses_explicit_parent_membership(db_with_reserve_collection_property) -> None:
    db = db_with_reserve_collection_property
    db.add_object(ClassEnum.Reserve, "TestReserve2")
    db.add_membership(
        parent_class_enum=ClassEnum.Reserve,
        child_class_enum=ClassEnum.Region,
        parent_object_name="TestReserve2",
        child_object_name="region-01",
        collection_enum=CollectionEnum.Regions,
    )
    db.add_property(
        ClassEnum.Region,
        "region-01",
        "Load Risk",
        7.0,
        collection_enum=CollectionEnum.Regions,
        parent_class_enum=ClassEnum.Reserve,
        parent_object_name="TestReserve2",
    )

    db.update_property(
        "region-01",
        "Load Risk",
        8.0,
        object_class=ClassEnum.Region,
        collection=CollectionEnum.Regions,
        parent_class=ClassEnum.Reserve,
        parent_object_name="TestReserve2",
    )

    rows = db.get_object_properties(
        ClassEnum.Region,
        "region-01",
        property_names="Load Risk",
        parent_class_enum=ClassEnum.Reserve,
        collection_enum=CollectionEnum.Regions,
    )
    assert sorted(property["value"] for property in rows) == [6.0, 8.0]


def test_update_property_explicit_parent_class_constrains_membership(
    db_with_reserve_collection_property,
) -> None:
    db = db_with_reserve_collection_property
    db.add_object(ClassEnum.Region, "TestReserve")
    db.add_membership(
        parent_class_enum=ClassEnum.Region,
        child_class_enum=ClassEnum.Region,
        parent_object_name="TestReserve",
        child_object_name="region-01",
        collection_enum=CollectionEnum.Regions,
    )
    db.add_property(
        ClassEnum.Region,
        "region-01",
        "Wheeling Charge",
        9.0,
        collection_enum=CollectionEnum.Regions,
        parent_class_enum=ClassEnum.Region,
        parent_object_name="TestReserve",
    )

    db.update_property(
        "region-01",
        "Wheeling Charge",
        10.0,
        object_class=ClassEnum.Region,
        collection=CollectionEnum.Regions,
        parent_class=ClassEnum.Region,
        parent_object_name="TestReserve",
    )

    region_rows = db.get_object_properties(
        ClassEnum.Region,
        "region-01",
        property_names="Wheeling Charge",
        parent_class_enum=ClassEnum.Region,
        collection_enum=CollectionEnum.Regions,
    )
    assert [property["value"] for property in region_rows] == [10.0]


def test_update_property_raises_for_missing_fixture_property(run_of_river_db: PlexosDB) -> None:
    with pytest.raises(NotFoundError):
        run_of_river_db.update_property(
            "Coal_Gen",
            "Max Capacity",
            625.0,
            object_class=ClassEnum.Generator,
            band=99,
        )
