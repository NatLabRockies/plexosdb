"""Checks used on plexosdb."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from loguru import logger

from .enums import ClassEnum, CollectionEnum, Schema
from .exceptions import NotFoundError
from .utils import normalize_names

if TYPE_CHECKING:
    from .db import PlexosDB

MEMBERSHIP_FROM_RECORD_FIELDS = {
    "parent_object_id",
    "child_object_id",
    "collection_id",
    "child_class_id",
    "parent_class_id",
}


def check_memberships_from_records(memberships: list[dict[str, int]]) -> bool:
    """Validate membership records have the exact required fields.

    Parameters
    ----------
    memberships : list[dict[str, int]]
        Membership dictionaries expected to contain exactly these keys:
        parent_object_id, child_object_id, collection_id, child_class_id,
        parent_class_id.

    Returns
    -------
    bool
        True when all records contain exactly the expected keys, otherwise False.
    """
    return all(record.keys() == MEMBERSHIP_FROM_RECORD_FIELDS for record in memberships)


def check_attribute_exists(
    db: PlexosDB, attribute_name: str, /, *, object_name: str, object_class: ClassEnum
) -> bool:
    """Check if an attribute exists for a specific object.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    attribute_name : str
        Name of the attribute to validate.
    object_name : str
        Name of the target object.
    object_class : ClassEnum
        Class for the target object.

    Returns
    -------
    bool
        True if the attribute exists for the object.

    Notes
    -----
    This check is not yet implemented.
    """
    query = """
        SELECT 1
        FROM t_attribute_data AS data
        JOIN t_object AS obj ON obj.object_id = data.object_id
        JOIN t_attribute AS attr ON attr.attribute_id = data.attribute_id
        JOIN t_class AS class ON class.class_id = obj.class_id
        WHERE obj.name = ?
        AND class.name = ?
        AND attr.name = ?
        AND attr.class_id = obj.class_id
        LIMIT 1
    """
    return bool(db._db.query(query, (object_name, object_class, attribute_name)))


def check_class_exists(db: PlexosDB, class_enum: ClassEnum) -> bool:
    """Check if a class exists in the database.

    Determines whether a class with the given enumeration exists in the schema.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    class_enum : ClassEnum
        Class enumeration to check.

    Returns
    -------
    bool
        True if the class exists, False otherwise.

    See Also
    --------
    PlexosDB.get_class_id : Get the ID for a class.
    PlexosDB.list_classes : List all available classes.
    """
    query = f"SELECT 1 FROM {Schema.Class.name} WHERE name = ?"
    return bool(db._db.query(query, (class_enum,)))


def check_category_exists(db: PlexosDB, class_enum: ClassEnum, name: str) -> bool:
    """Check if a category exists for a specific class.

    Determines whether a category with the given name exists for the specified
    class.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    class_enum : ClassEnum
        Class enumeration to check the category for.
    name : str
        Name of the category to check.

    Returns
    -------
    bool
        True if the category exists, False otherwise.

    Raises
    ------
    NotFoundError
        If class_enum does not exist in the database. This indicates a
        programming error because categories are class-scoped.
    """
    if not check_class_exists(db, class_enum):
        msg = (
            f"Class '{class_enum}' does not exist. "
            "Cannot check category for non-existent class. "
            "Use `list_classes()` to see available classes."
        )
        raise NotFoundError(msg)

    query = f"SELECT 1 FROM {Schema.Categories.name} WHERE name = ? AND class_id = ?"
    class_id = db.get_class_id(class_enum)
    return bool(db._db.query(query, (name, class_id)))


def check_collection_exists(
    db: PlexosDB,
    collection_enum: CollectionEnum,
    /,
    *,
    parent_class: ClassEnum | None = None,
    child_class: ClassEnum | None = None,
) -> bool:
    """Check if a collection exists in the database.

    Determines whether a collection with the given enumeration exists,
    optionally filtered by parent and/or child class.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    collection_enum : CollectionEnum
        Collection enumeration to check.
    parent_class : ClassEnum | None, optional
        Parent class enumeration to filter by.
    child_class : ClassEnum | None, optional
        Child class enumeration to filter by.

    Returns
    -------
    bool
        True if the collection exists (matching all specified criteria),
        False otherwise.

    Raises
    ------
    NotFoundError
        If parent_class or child_class is specified but does not exist.

    Notes
    -----
    The method returns False only when the collection itself does not exist or
    does not match the requested class filter.
    """
    conditions = ["name = ?"]
    params: list[str | int] = [str(collection_enum)]

    if parent_class and not check_class_exists(db, parent_class):
        msg = (
            f"Parent class '{parent_class}' does not exist. "
            "Cannot search for collection with non-existent parent class. "
            "Use `list_classes()` to see available classes."
        )
        raise NotFoundError(msg)

    if parent_class:
        parent_class_id = db.get_class_id(parent_class)
        conditions.append("parent_class_id = ?")
        params.append(parent_class_id)

    if child_class is not None and not check_class_exists(db, child_class):
        msg = (
            f"Child class '{child_class}' does not exist. "
            "Cannot search for collection with non-existent child class. "
            "Use `list_classes()` to see available classes."
        )
        raise NotFoundError(msg)

    if child_class:
        child_class_id = db.get_class_id(child_class)
        conditions.append("child_class_id = ?")
        params.append(child_class_id)

    where_clause = " AND ".join(conditions)
    query = f"SELECT 1 FROM {Schema.Collection.name} WHERE {where_clause}"
    return bool(db._db.query(query, tuple(params)))


def check_data_id_exist(db: PlexosDB, data_id: int) -> bool:
    """Check that a data id is present on t_data table.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    data_id : int
        Data row identifier.

    Returns
    -------
    bool
        True when data_id exists in t_data, False otherwise.
    """
    query = "SELECT 1 FROM t_data where data_id = ?"
    return bool(db.query(query, (data_id,)))


def check_tag_exists(db: PlexosDB, data_id: int, object_id: int) -> bool:
    """Check if a tag exists linking a data record to an object.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    data_id : int
        Data ID to check.
    object_id : int
        Object ID to check.

    Returns
    -------
    bool
        True if a t_tag row exists for the pair (data_id, object_id),
        otherwise False.
    """
    query = "SELECT 1 FROM t_tag WHERE data_id = ? AND object_id = ?"
    return bool(db.query(query, (data_id, object_id)))


def check_membership_exists(
    db: PlexosDB,
    parent_object_name: str,
    child_object_name: str,
    /,
    *,
    parent_class: ClassEnum,
    child_class: ClassEnum,
    collection: CollectionEnum,
) -> bool:
    """Check if a membership exists between two objects.

    Determines whether a membership relationship exists between the specified
    parent and child objects within the given collection.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    parent_object_name : str
        Name of the parent object.
    child_object_name : str
        Name of the child object.
    parent_class : ClassEnum
        Class enumeration of the parent object.
    child_class : ClassEnum
        Class enumeration of the child object.
    collection : CollectionEnum
        Collection enumeration defining the relationship type.

    Returns
    -------
    bool
        True if the membership exists, False otherwise.

    Raises
    ------
    NotFoundError
        If parent class, child class, or collection filter is invalid.
    """
    if not check_class_exists(db, parent_class):
        msg = (
            f"Parent class '{parent_class}' does not exist. "
            "Cannot check membership for non-existent parent class. "
            "Use `list_classes()` to see available classes."
        )
        raise NotFoundError(msg)

    if not check_class_exists(db, child_class):
        msg = (
            f"Child class '{child_class}' does not exist. "
            "Cannot check membership for non-existent child class. "
            "Use `list_classes()` to see available classes."
        )
        raise NotFoundError(msg)

    if not check_collection_exists(db, collection, parent_class=parent_class, child_class=child_class):
        msg = (
            f"Collection '{collection}' does not exist for "
            f"parent_class={parent_class} and child_class={child_class}. "
            "Check available collections using `list_collections()`"
        )
        raise NotFoundError(msg)

    parent_object_id = db.get_object_id(parent_class, parent_object_name)
    child_object_id = db.get_object_id(child_class, child_object_name)
    collection_id = db.get_collection_id(collection, parent_class, child_class)

    query = """
    SELECT 1 FROM t_membership
    WHERE parent_object_id = ?
    AND child_object_id = ?
    AND collection_id = ?
    """
    result = bool(db._db.query(query, (parent_object_id, child_object_id, collection_id)))
    return bool(result)


def check_object_exists(
    db: PlexosDB, class_enum: ClassEnum, /, name: str, *, category: str | None = None
) -> bool:
    """Check if an object exists in the database.

    Determines whether an object with the given name and class exists,
    optionally filtered by category.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    class_enum : ClassEnum
        Class enumeration of the object.
    name : str
        Name of the object to check.
    category : str | None, optional
        Category name to filter by.

    Returns
    -------
    bool
        True if the object exists (and matches category if specified),
        False otherwise.

    Raises
    ------
    NotFoundError
        If class_enum does not exist in the database.
    """
    if not check_class_exists(db, class_enum):
        msg = (
            f"Class '{class_enum}' does not exist. "
            "Cannot check object for non-existent class. "
            "Use `list_classes()` to see available classes."
        )
        raise NotFoundError(msg)

    class_id = db.get_class_id(class_enum)
    if category is None:
        query = f"SELECT 1 FROM {Schema.Objects.name} WHERE name = ? AND class_id = ?"
        params: tuple[str, int] | tuple[str, int, str] = (name, class_id)
    else:
        query = f"""
        SELECT 1 FROM {Schema.Objects.name} obj
        JOIN {Schema.Categories.name} cat ON obj.category_id = cat.category_id
        WHERE obj.name = ? AND obj.class_id = ? AND cat.name = ?
        """
        params = (name, class_id, category)

    return bool(db._db.query(query, params))


def check_property_exists(
    db: PlexosDB,
    collection_enum: CollectionEnum,
    /,
    object_class: ClassEnum,
    property_names: str | Iterable[str],
    *,
    parent_class: ClassEnum | None = None,
) -> bool:
    """Check if properties exist for a specific collection and class.

    Verifies that all specified property names are valid for the given
    collection and class.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    collection_enum : CollectionEnum
        Collection enumeration the properties should belong to.
    object_class : ClassEnum
        Class enumeration of the object.
    property_names : str | Iterable[str]
        Property name or names to check.
    parent_class : ClassEnum | None, optional
        Class enumeration of the parent object.

    Returns
    -------
    bool
        True if all properties exist, False otherwise.

    Raises
    ------
    NotFoundError
        If parent class, child class, or collection filter is invalid.

    Notes
    -----
    If any property in the list is invalid, the function returns False and logs
    the invalid list.
    """
    if parent_class and not check_class_exists(db, parent_class):
        msg = (
            f"Parent class '{parent_class}' does not exist. "
            "Cannot check properties for non-existent parent class. "
            "Use `list_classes()` to see available classes."
        )
        raise NotFoundError(msg)

    if not check_class_exists(db, object_class):
        msg = (
            f"Child class '{object_class}' does not exist. "
            "Cannot check properties for non-existent child class. "
            "Use `list_classes()` to see available classes."
        )
        raise NotFoundError(msg)

    if not check_collection_exists(
        db,
        collection_enum,
        parent_class=parent_class or ClassEnum.System,
        child_class=object_class,
    ):
        msg = (
            f"Collection '{collection_enum}' does not exist for "
            f"parent_class={parent_class or ClassEnum.System} and child_class={object_class}. "
            "Check available collections using `list_collections()`"
        )
        raise NotFoundError(msg)

    property_names = normalize_names(property_names)
    valid_props = db.list_valid_properties(
        collection_enum,
        parent_class_enum=parent_class or ClassEnum.System,
        child_class_enum=object_class,
    )
    invalid = [prop for prop in property_names if prop not in valid_props]
    if invalid:
        logger.error("Invalid properties {} for collection {}", property_names, collection_enum)
        return False
    return True


def check_scenario_exists(db: PlexosDB, name: str) -> bool:
    """Check if a scenario exists in the database.

    Determines whether a scenario with the given name exists.

    Parameters
    ----------
    db : PlexosDB
        Database instance.
    name : str
        Name of the scenario to check.

    Returns
    -------
    bool
        True if the scenario exists, False otherwise.

    See Also
    --------
    PlexosDB.get_class_id : Get the ID for a class.
    ClassEnum.Scenario : Scenario class enumeration.
    """
    query = f"SELECT 1 FROM {Schema.Objects.name} WHERE name = ? AND class_id = ?"
    class_id = db.get_class_id(ClassEnum.Scenario)
    return bool(db._db.query(query, (name, class_id)))


def _check_attribute_exists_method(
    self: PlexosDB, attribute_name: str, /, *, object_name: str, object_class: ClassEnum
) -> bool:
    """Check if an attribute exists for a specific object."""
    return check_attribute_exists(self, attribute_name, object_name=object_name, object_class=object_class)


def _check_category_exists_method(self: PlexosDB, class_enum: ClassEnum, name: str) -> bool:
    """Check if a category exists for a specific class."""
    return check_category_exists(self, class_enum, name)


def _check_class_exists_method(self: PlexosDB, class_enum: ClassEnum) -> bool:
    """Check if a class exists in the database."""
    return check_class_exists(self, class_enum)


def _check_collection_exists_method(
    self: PlexosDB,
    collection_enum: CollectionEnum,
    /,
    *,
    parent_class: ClassEnum | None = None,
    child_class: ClassEnum | None = None,
) -> bool:
    """Check if a collection exists in the database."""
    return check_collection_exists(
        self,
        collection_enum,
        parent_class=parent_class,
        child_class=child_class,
    )


def _check_data_id_exist_method(self: PlexosDB, data_id: int) -> bool:
    """Check that a data id is present on t_data table."""
    return check_data_id_exist(self, data_id)


def _check_tag_exists_method(self: PlexosDB, data_id: int, object_id: int) -> bool:
    """Check if a tag exists linking a data record to an object."""
    return check_tag_exists(self, data_id, object_id)


def _check_membership_exists_method(
    self: PlexosDB,
    parent_object_name: str,
    child_object_name: str,
    /,
    *,
    parent_class: ClassEnum,
    child_class: ClassEnum,
    collection: CollectionEnum,
) -> bool:
    """Check if a membership exists between two objects."""
    return check_membership_exists(
        self,
        parent_object_name,
        child_object_name,
        parent_class=parent_class,
        child_class=child_class,
        collection=collection,
    )


def _check_object_exists_method(
    self: PlexosDB, class_enum: ClassEnum, /, name: str, *, category: str | None = None
) -> bool:
    """Check if an object exists in the database."""
    return check_object_exists(self, class_enum, name, category=category)


def _check_property_exists_method(
    self: PlexosDB,
    collection_enum: CollectionEnum,
    /,
    object_class: ClassEnum,
    property_names: str | Iterable[str],
    *,
    parent_class: ClassEnum | None = None,
) -> bool:
    """Check if properties exist for a specific collection and class."""
    return check_property_exists(
        self,
        collection_enum,
        object_class,
        property_names,
        parent_class=parent_class,
    )


def _check_scenario_exists_method(self: PlexosDB, name: str) -> bool:
    """Check if a scenario exists in the database."""
    return check_scenario_exists(self, name)


def register_plexosdb_check_methods(plexosdb_cls: type[PlexosDB]) -> None:
    """Attach check_* instance methods to PlexosDB from this module."""
    setattr(plexosdb_cls, "check_attribute_exists", _check_attribute_exists_method)
    setattr(plexosdb_cls, "check_category_exists", _check_category_exists_method)
    setattr(plexosdb_cls, "check_class_exists", _check_class_exists_method)
    setattr(plexosdb_cls, "check_collection_exists", _check_collection_exists_method)
    setattr(plexosdb_cls, "check_data_id_exist", _check_data_id_exist_method)
    setattr(plexosdb_cls, "check_tag_exists", _check_tag_exists_method)
    setattr(plexosdb_cls, "check_membership_exists", _check_membership_exists_method)
    setattr(plexosdb_cls, "check_object_exists", _check_object_exists_method)
    setattr(plexosdb_cls, "check_property_exists", _check_property_exists_method)
    setattr(plexosdb_cls, "check_scenario_exists", _check_scenario_exists_method)
