from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plexosdb.db import PlexosDB


def test_copy_object(db_base: PlexosDB, caplog):
    from plexosdb import ClassEnum

    db = db_base
    original_object_name = "TestGen"
    object_class = ClassEnum.Generator
    original_object_id = db.add_object(object_class, original_object_name)
    test_property_name = "Max Capacity"
    test_property_value = 100.0
    _ = db.add_property(
        ClassEnum.Generator,
        original_object_name,
        test_property_name,
        test_property_value,
    )

    new_object_name = "TestGenCopy"
    new_object_id = db.copy_object(object_class, original_object_name, new_object_name)
    assert new_object_id
    assert new_object_id != original_object_id
    assert "do not have any memberships" in caplog.text

    new_properties = db.get_object_properties(object_class, new_object_name)[0]
    old_properties = db.get_object_properties(object_class, original_object_name)[0]
    assert all(property_name in new_properties for property_name in old_properties.keys())
    for old_property in old_properties:
        if old_property == "name":
            assert new_properties[old_property] == new_object_name
        elif old_property == "object_id":
            assert new_properties[old_property] != original_object_id
        else:
            assert old_properties[old_property] == new_properties[old_property]


def test_copy_object_copies_date_from_and_date_to(db_base: PlexosDB):
    from plexosdb import ClassEnum

    db = db_base
    original_object_name = "TestGenDates"
    object_class = ClassEnum.Generator
    db.add_object(object_class, original_object_name)

    date_from = datetime(2026, 1, 1)
    date_to = datetime(2026, 12, 31)
    original_data_id = db.add_property(
        ClassEnum.Generator,
        original_object_name,
        "Max Capacity",
        100.0,
        date_from=date_from,
        date_to=date_to,
    )

    original_date_from = db.query("SELECT date FROM t_date_from WHERE data_id = ?", (original_data_id,))
    original_date_to = db.query("SELECT date FROM t_date_to WHERE data_id = ?", (original_data_id,))
    assert original_date_from == [(date_from.isoformat(),)]
    assert original_date_to == [(date_to.isoformat(),)]

    new_object_name = "TestGenDatesCopy"
    db.copy_object(object_class, original_object_name, new_object_name)

    new_data_ids = db.get_object_data_ids(object_class, name=new_object_name)
    assert len(new_data_ids) == 1
    new_data_id = new_data_ids[0]
    assert new_data_id != original_data_id

    copied_date_from = db.query("SELECT date FROM t_date_from WHERE data_id = ?", (new_data_id,))
    copied_date_to = db.query("SELECT date FROM t_date_to WHERE data_id = ?", (new_data_id,))
    assert copied_date_from == [(date_from.isoformat(),)]
    assert copied_date_to == [(date_to.isoformat(),)]


def test_copy_object_with_memberships(db_base: PlexosDB):
    from plexosdb import ClassEnum
    from plexosdb.enums import CollectionEnum

    db: PlexosDB = db_base
    object_name = "TestGen"
    object_class = ClassEnum.Generator
    _ = db.add_object(object_class, object_name)
    child_object_name = "TestNode"
    child_class = ClassEnum.Node
    _ = db.add_object(child_class, child_object_name)
    collection = CollectionEnum.Nodes

    membership_id_child = db.add_membership(
        object_class, child_class, object_name, child_object_name, collection
    )
    assert membership_id_child == db.get_membership_id(object_name, child_object_name, collection)

    new_object_name = "TestGen2"
    object_id = db.get_object_id(object_class, name=object_name)
    category_id = db.query("SELECT category_id from t_object WHERE object_id = ?", (object_id,))
    category = db.query("SELECT name from t_category WHERE category_id = ?", (category_id[0][0],))
    _ = db.add_object(object_class, new_object_name, category=category[0][0])

    membership_mapping = db.copy_object_memberships(object_class, object_name, new_object_name)
    new_child_membership = db.get_membership_id(new_object_name, child_object_name, collection)
    assert membership_id_child in membership_mapping
    assert membership_mapping[membership_id_child] == new_child_membership


def test_copy_object_copies_attributes(db_base: PlexosDB):
    from plexosdb import ClassEnum

    db = db_base
    object_class = ClassEnum.Generator

    original_object_name = "TestGenWithAttribute"
    new_object_name = "TestGenWithAttributeCopy"

    original_object_id = db.add_object(object_class, original_object_name)

    db.add_attributes_from_records(
        [
            {"name": original_object_name, "attribute": "Latitude", "value": 42.0},
            {"name": original_object_name, "attribute": "Longitude", "value": -105.0},
        ],
        object_class=object_class,
    )

    new_object_id = db.copy_object(object_class, original_object_name, new_object_name)

    old_rows = db._db.fetchall(
        """
        SELECT attr.name, data.value, data.state
        FROM t_attribute_data AS data
        JOIN t_attribute AS attr ON attr.attribute_id = data.attribute_id
        WHERE data.object_id = ?
        ORDER BY attr.name
        """,
        (original_object_id,),
    )

    new_rows = db._db.fetchall(
        """
        SELECT attr.name, data.value, data.state
        FROM t_attribute_data AS data
        JOIN t_attribute AS attr ON attr.attribute_id = data.attribute_id
        WHERE data.object_id = ?
        ORDER BY attr.name
        """,
        (new_object_id,),
    )

    assert old_rows == [
        ("Latitude", 42.0, None),
        ("Longitude", -105.0, None),
    ]
    assert new_rows == old_rows


def test_copy_object_without_attributes(db_base: PlexosDB):
    from plexosdb import ClassEnum

    db = db_base
    object_class = ClassEnum.Generator

    original_object_name = "TestGenNoAttr"
    new_object_name = "TestGenNoAttrCopy"

    original_object_id = db.add_object(object_class, original_object_name)
    new_object_id = db.copy_object(object_class, original_object_name, new_object_name)

    assert (
        db._db.fetchall(
            "SELECT * FROM t_attribute_data WHERE object_id = ?",
            (original_object_id,),
        )
        == []
    )
    assert (
        db._db.fetchall(
            "SELECT * FROM t_attribute_data WHERE object_id = ?",
            (new_object_id,),
        )
        == []
    )
