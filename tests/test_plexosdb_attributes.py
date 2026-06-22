from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from plexosdb.db import PlexosDB


def test_add_attribute(db_base: PlexosDB):
    from plexosdb.enums import ClassEnum

    db: PlexosDB = db_base
    attribute_id = db.get_attribute_id(ClassEnum.Generator, "Latitude")
    assert attribute_id
    assert attribute_id == 1

    _ = db.add_object(ClassEnum.Generator, "TestGen")
    attribute_id_insert = db.add_attribute(
        ClassEnum.Generator, "TestGen", attribute_name="Latitude", attribute_value=10.1
    )

    assert attribute_id == attribute_id_insert

    result = db.get_attribute(ClassEnum.Generator, object_name="TestGen", attribute_name="Latitude")[0]
    assert result
    assert result == 10.1


def test_add_attribute_returns_attribute_id(db_base: PlexosDB):
    """Return the attribute definition ID rather than an insert-success flag."""
    from plexosdb.enums import ClassEnum

    db: PlexosDB = db_base
    db.add_object(ClassEnum.Generator, "TestGen")

    attribute_id = db.get_attribute_id(ClassEnum.Generator, "Longitude")
    result = db.add_attribute(
        ClassEnum.Generator,
        "TestGen",
        attribute_name="Longitude",
        attribute_value=10.1,
    )

    assert type(result) is int
    assert result == attribute_id


def test_list_attributes(db_base: PlexosDB):
    from plexosdb.enums import ClassEnum

    db: PlexosDB = db_base

    result = db.list_attributes(ClassEnum.Generator)
    assert result
    assert len(result) == 2


def test_get_attributes_returns_assigned_values(db_with_model_attributes: PlexosDB):
    """Return assigned attributes for one object only."""
    from plexosdb import ClassEnum

    db = db_with_model_attributes
    db.add_object(ClassEnum.Model, "Model1")
    db.add_object(ClassEnum.Model, "Model2")
    db.add_attributes_from_records(
        [
            {"name": "Model1", "attribute": "Enabled", "value": -1, "state": 1},
            {"name": "Model1", "attribute": "Random Number Seed", "value": 1000},
            {"name": "Model2", "attribute": "Enabled", "value": 0},
        ],
        object_class=ClassEnum.Model,
    )

    result = db.get_attributes("Model1", object_class=ClassEnum.Model)

    assert result == [
        {"name": "Model1", "attribute": "Enabled", "value": -1.0, "state": 1},
        {
            "name": "Model1",
            "attribute": "Random Number Seed",
            "value": 1000.0,
            "state": None,
        },
    ]


def test_get_attributes_filters_by_attribute_names(
    db_with_model_attributes: PlexosDB,
):
    """Filter assigned attributes by name."""
    from plexosdb import ClassEnum

    db = db_with_model_attributes
    db.add_object(ClassEnum.Model, "Model1")
    db.add_attributes_from_records(
        [{"name": "Model1", "Enabled": -1, "Random Number Seed": 1000}],
        object_class=ClassEnum.Model,
    )

    single_result = db.get_attributes(
        "Model1",
        object_class=ClassEnum.Model,
        attribute_names="Enabled",
    )
    assert [record["attribute"] for record in single_result] == ["Enabled"]

    multiple_result = db.get_attributes(
        "Model1",
        object_class=ClassEnum.Model,
        attribute_names=["Random Number Seed", "Enabled"],
    )
    assert [record["attribute"] for record in multiple_result] == [
        "Enabled",
        "Random Number Seed",
    ]


def test_get_attributes_returns_empty_list_without_assignments(
    db_with_model_attributes: PlexosDB,
):
    """Return an empty list when an object has no assigned attributes."""
    from plexosdb import ClassEnum

    db = db_with_model_attributes
    db.add_object(ClassEnum.Model, "Model1")

    assert db.get_attributes("Model1", object_class=ClassEnum.Model) == []


def test_get_attributes_fails_with_nonexistent_object(
    db_with_model_attributes: PlexosDB,
):
    """Raise NotFoundError when the object does not exist."""
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NotFoundError

    with pytest.raises(NotFoundError, match="Object = `MissingModel` does not exist"):
        db_with_model_attributes.get_attributes(
            "MissingModel",
            object_class=ClassEnum.Model,
        )


def test_delete_attribute_removes_single_attribute(db_with_model_attributes: PlexosDB):
    """Delete one attribute value without removing other attributes."""
    from plexosdb import ClassEnum

    db = db_with_model_attributes
    db.add_object(ClassEnum.Model, "Model1")

    db.add_attributes_from_records(
        [{"name": "Model1", "Enabled": -1, "Random Number Seed": 1000}],
        object_class=ClassEnum.Model,
    )

    db.delete_attribute("Enabled", object_name="Model1", object_class=ClassEnum.Model)

    rows = db._db.fetchall(
        """
        SELECT attr.name, data.value
        FROM t_attribute_data AS data
        JOIN t_attribute AS attr ON attr.attribute_id = data.attribute_id
        JOIN t_object AS obj ON obj.object_id = data.object_id
        WHERE obj.name = ?
        ORDER BY attr.name
        """,
        ("Model1",),
    )

    assert rows == [("Random Number Seed", 1000.0)]


def test_delete_attribute_does_not_affect_other_objects(db_with_model_attributes: PlexosDB):
    """Delete an attribute from one object without changing another object."""
    from plexosdb import ClassEnum

    db = db_with_model_attributes
    db.add_object(ClassEnum.Model, "Model1")
    db.add_object(ClassEnum.Model, "Model2")

    db.add_attributes_from_records(
        [
            {"name": "Model1", "Enabled": -1},
            {"name": "Model2", "Enabled": -1},
        ],
        object_class=ClassEnum.Model,
    )

    db.delete_attribute("Enabled", object_name="Model1", object_class=ClassEnum.Model)

    rows = db._db.fetchall(
        """
        SELECT obj.name, attr.name, data.value
        FROM t_attribute_data AS data
        JOIN t_attribute AS attr ON attr.attribute_id = data.attribute_id
        JOIN t_object AS obj ON obj.object_id = data.object_id
        ORDER BY obj.name, attr.name
        """
    )

    assert rows == [("Model2", "Enabled", -1.0)]


def test_delete_attribute_fails_with_nonexistent_object(db_with_model_attributes: PlexosDB):
    """Raise NotFoundError when deleting an attribute from a missing object."""
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NotFoundError

    db = db_with_model_attributes

    with pytest.raises(NotFoundError, match="Object = `MissingModel` does not exist"):
        db.delete_attribute("Enabled", object_name="MissingModel", object_class=ClassEnum.Model)


def test_delete_attribute_fails_with_nonexistent_attribute_value(
    db_with_model_attributes: PlexosDB,
):
    """Raise NotFoundError when the object has no value for the attribute."""
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NotFoundError

    db = db_with_model_attributes
    db.add_object(ClassEnum.Model, "Model1")

    with pytest.raises(NotFoundError, match="Attribute 'Enabled' not found for object 'Model1'"):
        db.delete_attribute("Enabled", object_name="Model1", object_class=ClassEnum.Model)


def test_delete_attribute_fails_with_undefined_attribute(
    db_with_model_attributes: PlexosDB,
):
    """Raise NotFoundError when the attribute is undefined for the object's class."""
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NotFoundError

    db = db_with_model_attributes
    db.add_object(ClassEnum.Model, "Model1")

    with pytest.raises(
        NotFoundError,
        match="Attribute 'Non_Valid_Attribute' not found for class 'Model'",
    ):
        db.delete_attribute(
            "Non_Valid_Attribute",
            object_name="Model1",
            object_class=ClassEnum.Model,
        )
