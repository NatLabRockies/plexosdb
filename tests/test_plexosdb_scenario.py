from __future__ import annotations

from datetime import datetime
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


def test_create_object_scenario_preserves_qualified_records_when_overriding(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    object_name = "Qualified Scenario Generator"
    db_base.add_object(ClassEnum.Generator, object_name)
    db_base.add_object(ClassEnum.Variable, "ScenarioVariable")
    first_data_id = db_base.add_property(
        ClassEnum.Generator,
        object_name,
        "Max Capacity",
        100.0,
        scenario="Base Case",
        band=1,
        date_from=datetime(2025, 1, 1),
        date_to=datetime(2025, 1, 31, 23),
        datafile_text="source-one.csv",
        timeslice="Peak",
    )
    second_data_id = db_base.add_property(
        ClassEnum.Generator,
        object_name,
        "Max Capacity",
        200.0,
        scenario="Base Case",
        band=2,
        date_from=datetime(2025, 2, 1),
        date_to=datetime(2025, 2, 28, 23),
        datafile_text="source-two.csv",
        timeslice="Off-Peak",
    )
    db_base.add_variable_tag(first_data_id, "ScenarioVariable")
    db_base._db.execute(
        "UPDATE t_text SET state = 3 WHERE data_id = ? AND value = 'source-one.csv'",
        (first_data_id,),
    )

    scenario_id = db_base.create_object_scenario(
        object_name,
        "Qualified Override",
        {"Max Capacity": 250.0},
        object_class=ClassEnum.Generator,
        base_scenario="Base Case",
    )
    membership_id = db_base.get_memberships_system(object_name, object_class=ClassEnum.Generator)[0][
        "membership_id"
    ]
    property_id = db_base.get_property_id(
        "Max Capacity",
        collection_enum=CollectionEnum.Generators,
        child_class_enum=ClassEnum.Generator,
        parent_class_enum=ClassEnum.System,
    )
    datafile_class_id = db_base.get_class_id(ClassEnum.DataFile)
    timeslice_class_id = db_base.get_class_id(ClassEnum.Timeslice)
    variable_class_id = db_base.get_class_id(ClassEnum.Variable)
    rows = db_base.query(
        """
        SELECT d.value,
               band.band_id,
               date_from.date,
               date_to.date,
               (SELECT text.value FROM t_text AS text
                WHERE text.data_id = d.data_id AND text.class_id = ?) AS datafile_text,
               (SELECT text.value FROM t_text AS text
                WHERE text.data_id = d.data_id AND text.class_id = ?) AS timeslice_text,
               (SELECT object.name
                FROM t_tag AS variable_tag
                JOIN t_object AS object ON object.object_id = variable_tag.object_id
                WHERE variable_tag.data_id = d.data_id
                  AND object.class_id = ?) AS variable_name,
               (SELECT text.state FROM t_text AS text
                WHERE text.data_id = d.data_id AND text.class_id = ?) AS datafile_state
        FROM t_data AS d
        JOIN t_tag AS scenario_tag
          ON scenario_tag.data_id = d.data_id AND scenario_tag.object_id = ?
        LEFT JOIN t_band AS band ON band.data_id = d.data_id
        LEFT JOIN t_date_from AS date_from ON date_from.data_id = d.data_id
        LEFT JOIN t_date_to AS date_to ON date_to.data_id = d.data_id
        WHERE d.membership_id = ? AND d.property_id = ?
        ORDER BY band.band_id
        """,
        (
            datafile_class_id,
            timeslice_class_id,
            variable_class_id,
            datafile_class_id,
            scenario_id,
            membership_id,
            property_id,
        ),
    )

    assert rows == [
        (
            250.0,
            1,
            "2025-01-01T00:00:00",
            "2025-01-31T23:00:00",
            "source-one.csv",
            "Peak",
            "ScenarioVariable",
            3,
        ),
        (
            250.0,
            2,
            "2025-02-01T00:00:00",
            "2025-02-28T23:00:00",
            "source-two.csv",
            "Off-Peak",
            None,
            None,
        ),
    ]
    assert db_base.query(
        "SELECT COUNT(*) FROM t_tag WHERE data_id IN (?, ?)",
        (first_data_id, second_data_id),
    ) == [(3,)]


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
