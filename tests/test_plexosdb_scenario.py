from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from plexosdb.db import PlexosDB


def test_adding_scenaro(db_base: PlexosDB):
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NameError

    db: PlexosDB = db_base

    test_scenario = "Test"
    object_id = db.add_scenario(test_scenario)
    assert object_id

    scenario_id = db.get_scenario_id(test_scenario)
    assert object_id == scenario_id

    test_scenario = "Test"
    with pytest.raises(NameError):
        _ = db.add_scenario(test_scenario)

    test_object_name = "TestGen"
    test_property_name = "Max Capacity"
    test_property_value = 100.0
    _ = db.add_object(ClassEnum.Generator, test_object_name)
    data_id = db.add_property(
        ClassEnum.Generator, test_object_name, test_property_name, test_property_value, scenario=test_scenario
    )
    assert data_id


def test_create_object_scenario_inherits_and_overrides_properties(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum

    object_name = "Scenario Generator"
    db_base.add_object(ClassEnum.Generator, object_name)
    db_base.add_property(ClassEnum.Generator, object_name, "Max Capacity", 100.0, scenario="Base Case")
    db_base.add_property(ClassEnum.Generator, object_name, "Min Stable Level", 10.0, scenario="Base Case")

    scenario_id = db_base.create_object_scenario(
        object_name,
        "High Demand",
        {"Max Capacity": 120.0},
        object_class=ClassEnum.Generator,
        description="High demand assumptions",
        base_scenario="Base Case",
    )

    records = db_base.get_object_properties(ClassEnum.Generator, object_name, scenario="High Demand")
    properties = {record["property"]: record["value"] for record in records}
    description = db_base._db.fetchone(
        "SELECT description FROM t_object WHERE object_id = ?",
        (scenario_id,),
    )
    assert properties == {"Max Capacity": 120.0, "Min Stable Level": 10.0}
    assert description == ("High demand assumptions",)


def test_create_object_scenario_rolls_back_invalid_property(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NameError

    object_name = "Scenario Generator"
    db_base.add_object(ClassEnum.Generator, object_name)

    with pytest.raises(NameError):
        db_base.create_object_scenario(
            object_name,
            "Invalid Scenario",
            {"Not a valid property": 1},
            object_class=ClassEnum.Generator,
        )

    assert not db_base.check_scenario_exists("Invalid Scenario")


def test_create_object_scenario_requires_existing_base_scenario(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NotFoundError

    object_name = "Scenario Generator"
    db_base.add_object(ClassEnum.Generator, object_name)

    with pytest.raises(NotFoundError, match="Base scenario"):
        db_base.create_object_scenario(
            object_name,
            "New Scenario",
            {},
            object_class=ClassEnum.Generator,
            base_scenario="Missing Base",
        )

    assert not db_base.check_scenario_exists("New Scenario")


def test_update_scenario_renames_and_updates_category_and_description(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum

    scenario_id = db_base.add_scenario("Old Scenario")
    db_base.add_category(ClassEnum.Scenario, "Planning")

    result = db_base.update_scenario(
        "Old Scenario",
        new_name="Updated Scenario",
        new_category="Planning",
        new_description="Updated scenario details",
    )

    row = db_base._db.fetchone(
        """
        SELECT object.name, category.name, object.description
        FROM t_object AS object
        JOIN t_category AS category ON category.category_id = object.category_id
        WHERE object.object_id = ?
        """,
        (scenario_id,),
    )
    assert result is None
    assert row == ("Updated Scenario", "Planning", "Updated scenario details")
    assert not db_base.check_scenario_exists("Old Scenario")
    assert db_base.check_scenario_exists("Updated Scenario")


def test_update_scenario_requires_existing_scenario(db_base: PlexosDB) -> None:
    from plexosdb.exceptions import NotFoundError

    with pytest.raises(NotFoundError, match="does not exist"):
        db_base.update_scenario("Missing Scenario", new_name="Renamed Scenario")
