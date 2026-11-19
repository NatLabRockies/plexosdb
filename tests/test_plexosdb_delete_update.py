from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from plexosdb import PlexosDB


def test_delete_category_is_class_scoped(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NotFoundError

    db_base.add_category(ClassEnum.Generator, "Category to delete")
    node_category_id = db_base.add_category(ClassEnum.Node, "Category to delete")

    db_base.delete_category("Category to delete", class_name=ClassEnum.Generator)

    assert not db_base.check_category_exists(ClassEnum.Generator, "Category to delete")
    assert db_base.get_category_id(ClassEnum.Node, "Category to delete") == node_category_id
    with pytest.raises(NotFoundError):
        db_base.delete_category("Category to delete", class_name=ClassEnum.Generator)


def test_delete_category_rejects_categories_assigned_to_objects(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum

    db_base.add_object(ClassEnum.Generator, "Category User", category="In Use")

    with pytest.raises(ValueError, match="objects still use it"):
        db_base.delete_category("In Use", class_name=ClassEnum.Generator)

    assert db_base.check_category_exists(ClassEnum.Generator, "In Use")


def test_delete_membership_cascades_data_and_membership_metadata(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum, CollectionEnum
    from plexosdb.exceptions import NotFoundError

    object_name = "Membership User"
    db_base.add_object(ClassEnum.Generator, object_name)
    db_base.add_property(ClassEnum.Generator, object_name, "Max Capacity", 50.0)
    membership_id = db_base.get_membership_id("System", object_name, CollectionEnum.Generators)
    data_count = db_base._db.fetchone("SELECT COUNT(*) FROM t_data WHERE membership_id = ?", (membership_id,))
    assert data_count == (1,)
    db_base.add_metadata(
        "membership",
        membership_id,
        "Test",
        "Note",
        "metadata",
    )

    db_base.delete_membership(
        "System",
        object_name,
        parent_class=ClassEnum.System,
        child_class=ClassEnum.Generator,
        collection=CollectionEnum.Generators,
    )

    assert (
        db_base._db.fetchone("SELECT 1 FROM t_membership WHERE membership_id = ?", (membership_id,)) is None
    )
    assert db_base._db.fetchone("SELECT 1 FROM t_data WHERE membership_id = ?", (membership_id,)) is None
    assert (
        db_base._db.fetchone(
            "SELECT 1 FROM t_membership_meta WHERE membership_id = ?",
            (membership_id,),
        )
        is None
    )
    with pytest.raises(NotFoundError, match="does not exist"):
        db_base.delete_membership(
            "System",
            object_name,
            parent_class=ClassEnum.System,
            child_class=ClassEnum.Generator,
            collection=CollectionEnum.Generators,
        )


def test_update_attribute_changes_value_and_preserves_state(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum

    object_name = "Attribute User"
    db_base.add_object(ClassEnum.Generator, object_name)
    attribute_id = db_base.add_attribute(
        ClassEnum.Generator,
        object_name,
        attribute_name="Latitude",
        attribute_value=1.5,
    )
    object_id = db_base.get_object_id(ClassEnum.Generator, object_name)
    db_base._db.execute(
        "UPDATE t_attribute_data SET state = ? WHERE object_id = ? AND attribute_id = ?",
        (7, object_id, attribute_id),
    )

    db_base.update_attribute(
        "Latitude",
        2.5,
        object_name=object_name,
        object_class=ClassEnum.Generator,
    )

    assert db_base._db.fetchone(
        "SELECT value, state FROM t_attribute_data WHERE object_id = ? AND attribute_id = ?",
        (object_id, attribute_id),
    ) == (2.5, 7)


def test_update_attribute_requires_existing_assignment(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NotFoundError

    db_base.add_object(ClassEnum.Generator, "No Attribute User")

    with pytest.raises(NotFoundError, match="not assigned"):
        db_base.update_attribute(
            "Latitude",
            2.5,
            object_name="No Attribute User",
            object_class=ClassEnum.Generator,
        )


def test_update_category_renames_and_preserves_object_assignment(db_base: PlexosDB) -> None:
    from plexosdb import ClassEnum

    object_name = "Category Rename User"
    db_base.add_object(ClassEnum.Generator, object_name, category="Old category")
    db_base.add_category(ClassEnum.Generator, "Existing category")

    db_base.update_category("Old category", "Renamed category", class_name=ClassEnum.Generator)

    assert db_base._db.fetchone(
        """
        SELECT category.name
        FROM t_object AS object
        JOIN t_category AS category ON category.category_id = object.category_id
        WHERE object.name = ?
        """,
        (object_name,),
    ) == ("Renamed category",)
    with pytest.raises(ValueError, match="already exists"):
        db_base.update_category("Renamed category", "Existing category", class_name=ClassEnum.Generator)
