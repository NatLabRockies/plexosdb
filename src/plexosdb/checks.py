"""Checks used on plexosdb."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Hashable, Iterable
from contextlib import closing
from functools import cache
from importlib.resources import files
import sqlite3
from typing import TYPE_CHECKING

from loguru import logger

from .db_constants import (
    MEMBERSHIP_FROM_RECORD_FIELDS,
    SQLITE_INTEGRITY_QUERY,
    FOREIGN_KEY_CHECK_QUERY,
    TABLE_NAMES_QUERY,
    TABLE_INFO_QUERY,
    RELATIONSHIP_FINDINGS_QUERY,
    CATEGORY_CLASS_FINDINGS_QUERY,
    PROPERTY_COLLECTION_FINDINGS_QUERY,
    STATIC_PROPERTY_ARTIFACTS_QUERY,
    DUPLICATE_STATIC_DATA_QUERY,
    DATA_GRAPHS_QUERY,
    DATA_GRAPH_TAGS_QUERY,
    DATA_GRAPH_TEXTS_QUERY,
    DUPLICATE_UIDS_QUERY,
    ORPHANED_CHILD_ROWS_QUERY,
    ATTRIBUTE_CLASS_FINDINGS_QUERY,
    SYSTEM_MEMBERSHIP_FINDINGS_QUERY,
    MEMBERSHIP_COUNT_BOUNDS_QUERY,
    VALID_TAG_CLASS_LANG_IDS,
    TAG_OBJECT_CLASS_QUERY,
    VARIABLE_CLASS_LANG_ID,
    ACTION_TAG_FINDINGS_QUERY,
    ACTION_TEXT_FINDINGS_QUERY,
    BAND_COUNT_FINDINGS_QUERY,
    REPAIR_MEMBERSHIP_CLASS_IDS_SCRIPT,
)
from .enums import ClassEnum, CollectionEnum, Schema
from .exceptions import DatabaseValidationCategory, DatabaseValidationFinding, NotFoundError
from .types import SQLiteValue
from .utils import no_space, normalize_names

if TYPE_CHECKING:
    from .db import PlexosDB
    from .db_manager import SQLiteManager


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
        True if the object has an assigned value for the attribute.
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


@cache
def get_default_schema_columns() -> tuple[tuple[str, frozenset[str]], ...]:
    """Return table columns introspected from the packaged PLEXOS schema."""
    schema_sql = files("plexosdb").joinpath("schema.sql").read_text(encoding="utf-8-sig")
    with closing(sqlite3.connect(":memory:")) as schema_db:
        schema_db.create_collation("NOSPACE", no_space)
        schema_db.executescript(schema_sql)
        table_names = [
            row[0] for row in schema_db.execute(TABLE_NAMES_QUERY) if not row[0].startswith("sqlite_")
        ]
        return tuple(
            (
                table,
                frozenset(row[1] for row in schema_db.execute(TABLE_INFO_QUERY.substitute(table=table))),
            )
            for table in table_names
        )


def find_database_schema_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Compare database tables and columns with the packaged PLEXOS schema."""
    available_tables = set(db.tables)
    findings: list[DatabaseValidationFinding] = []
    for table, expected_columns in get_default_schema_columns():
        if table not in available_tables:
            findings.append(
                DatabaseValidationFinding(
                    category=DatabaseValidationCategory.SCHEMA,
                    message=f"Required table {table!r} is missing.",
                )
            )
            continue

        available_columns = {row[1] for row in db.query(TABLE_INFO_QUERY.substitute(table=table))}
        missing_columns = sorted(expected_columns.difference(available_columns))
        for column in missing_columns:
            findings.append(
                DatabaseValidationFinding(
                    category=DatabaseValidationCategory.SCHEMA,
                    message=f"Required column '{table}.{column}' is missing.",
                )
            )
    return findings


def find_database_validation_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Collect database integrity and cross-table consistency findings."""
    findings = find_sqlite_integrity_issues(db)
    schema_findings = find_database_schema_issues(db)
    findings.extend(schema_findings)
    if schema_findings:
        return findings

    findings.extend(find_foreign_key_issues(db))
    findings.extend(find_database_relationship_issues(db))
    for find_issues in (
        _find_category_class_issues,
        _find_property_collection_mismatch_issues,
        _find_static_property_artifacts_issues,
        _find_duplicate_static_data_issues,
        _find_duplicate_data_graphs_issues,
        _find_duplicate_uids_issues,
        _find_orphaned_child_rows_issues,
        _find_attribute_class_issues,
        _find_system_membership_existence_issues,
        _find_membership_count_bounds_issues,
        _find_tag_object_class_issues,
        _find_action_only_on_variables_issues,
        _find_band_count_issues,
        _find_property_values_issues,
        _find_attribute_values_issues,
        _find_case_insensitive_name_collisions_issues,
        _find_custom_column_class_issues,
    ):
        issues = find_issues(db)
        if issues is not None:
            findings.extend(issues)
    return findings


def _find_category_class_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that t_object.class_id matches t_category.class_id."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.OBJECTS,
            message=(
                f"Category mismatch: Object '{name}' (object_id={oid}) "
                f"has class_id={obj_cid} but category '{cname}' has class_id={cat_cid}. "
                "Fix: reset category to the default '-' category for this class."
            ),
        )
        for oid, name, obj_cid, cat_cid, cname in db.query(CATEGORY_CLASS_FINDINGS_QUERY)
    ]


def _find_property_collection_mismatch_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that property and membership collection IDs must match for t_data."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Property-collection mismatch: data_id={did}, "
                f"property '{pname}' collection_id={pcid} != membership collection_id={mcid}. "
                "Fix: remove the invalid data row."
            ),
        )
        for did, pname, pcid, mcid in db.query(PROPERTY_COLLECTION_FINDINGS_QUERY)
    ]


def _find_static_property_artifacts_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that static properties must not have tags, texts, dates, or memo."""
    findings: list[DatabaseValidationFinding] = []
    for table_name, artifact_type in (
        ("t_tag", "tag"),
        ("t_text", "text"),
        ("t_date_from", "date_from"),
        ("t_date_to", "date_to"),
        ("t_memo_data", "memo"),
    ):
        for pid, pname, count in db.query(STATIC_PROPERTY_ARTIFACTS_QUERY.substitute(table=table_name)):
            findings.append(
                DatabaseValidationFinding(
                    category=DatabaseValidationCategory.PROPERTIES,
                    message=(
                        f"Static property with {artifact_type}: '{pname}' (property_id={pid}) "
                        f"is static but has {count} {table_name} row(s). "
                        f"Fix: set is_dynamic=1 on this property, or remove the {table_name} rows."
                    ),
                )
            )
    return findings


def _find_duplicate_static_data_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that static properties allow one data row per membership, property, and band."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Duplicated static data: membership_id={mid}, property_id={pid}, "
                f"band_id={bid}, count={count}. "
                "Fix: remove duplicate data rows, keeping only the last."
            ),
        )
        for mid, pid, bid, count in db.query(DUPLICATE_STATIC_DATA_QUERY)
    ]


def _find_duplicate_data_graphs_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that data rows with identical full property graphs are detected."""
    tags: dict[int, set[tuple[SQLiteValue, SQLiteValue]]] = defaultdict(set)
    for data_id, object_id, action_id in db.iter_query(DATA_GRAPH_TAGS_QUERY):
        tags[data_id].add((object_id, action_id or 0))

    texts: dict[int, set[tuple[SQLiteValue, SQLiteValue, SQLiteValue]]] = defaultdict(set)
    for data_id, class_id, value, action_id in db.iter_query(DATA_GRAPH_TEXTS_QUERY):
        texts[data_id].add((class_id, value, action_id or 0))

    fingerprints: dict[tuple[Hashable, ...], list[int]] = defaultdict(list)
    for data_id, membership_id, property_id, value, band_id, date_from, date_to, memo in db.iter_query(
        DATA_GRAPHS_QUERY
    ):
        fingerprint = (
            membership_id,
            property_id,
            value,
            band_id,
            frozenset(tags.pop(data_id, ())),
            frozenset(texts.pop(data_id, ())),
            date_from,
            date_to,
            memo,
        )
        fingerprints[fingerprint].append(data_id)

    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Duplicated data graph: {len(data_ids)} identical data rows "
                f"(data_ids={data_ids}) for membership_id={fingerprint[0]}, "
                f"property_id={fingerprint[1]}. "
                "Fix: remove the duplicate data rows."
            ),
        )
        for fingerprint, data_ids in fingerprints.items()
        if len(data_ids) > 1
    ]


def _find_duplicate_uids_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that every non-NULL t_data.uid must be unique."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Duplicated UID: uid={uid} appears {count} times in t_data. "
                "Fix: assign new unique UIDs to the duplicate rows."
            ),
        )
        for uid, count in db.query(DUPLICATE_UIDS_QUERY)
    ]


def _find_orphaned_child_rows_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Detect child rows pointing to non-existent t_data rows.

    Deleting data with foreign-key enforcement disabled can leave child rows
    behind because ON DELETE CASCADE does not fire. Report these orphans without
    deleting them.
    """
    findings: list[DatabaseValidationFinding] = []
    for table_name, label in (
        ("t_tag", "tag"),
        ("t_text", "text"),
        ("t_date_from", "date_from"),
        ("t_date_to", "date_to"),
        ("t_band", "band"),
        ("t_memo_data", "memo"),
    ):
        count = 0
        sample: list[int] = []
        for (data_id,) in db.iter_query(ORPHANED_CHILD_ROWS_QUERY.substitute(table=table_name)):
            count += 1
            if count <= 10:
                sample.append(data_id)
        if not count:
            continue
        more = f" (+{count - 10} more)" if count > 10 else ""
        findings.append(
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.PROPERTIES,
                message=(
                    f"Orphaned {label} rows: {count} row(s) in {table_name} "
                    f"reference non-existent data_ids {sample}{more}. "
                    f"Fix: DELETE FROM {table_name} WHERE data_id NOT IN (SELECT data_id FROM t_data)."
                ),
            )
        )
    return findings


def _find_attribute_class_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that t_attribute.class_id must match t_object.class_id."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.ATTRIBUTES,
            message=(
                f"Attribute-class mismatch: attribute '{aname}' (class_id={acid}) "
                f"on object '{oname}' (class_id={ocid}). "
                "Fix: remove the invalid attribute_data row."
            ),
        )
        for aname, acid, oname, ocid in db.query(ATTRIBUTE_CLASS_FINDINGS_QUERY)
    ]


def _find_system_membership_existence_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that every object except object_id=1 needs a System membership."""
    system_class = db.query("SELECT class_id FROM t_class WHERE lang_id = 1")
    if not system_class:
        return []

    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.MEMBERSHIPS,
            message=(
                f"Missing system membership: Object '{name}' (object_id={oid}) "
                "has no system membership. "
                "Fix: create a system membership with the correct collection for this class."
            ),
        )
        for oid, name in db.query(SYSTEM_MEMBERSHIP_FINDINGS_QUERY, (system_class[0][0],))
    ]


def _find_membership_count_bounds_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that membership count per parent must not exceed collection limits."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.MEMBERSHIPS,
            message=(
                f"Membership count exceeded: collection '{coll_name}' "
                f"(collection_id={coll_id}) allows max {max_allowed}, "
                f"but parent_object_id={parent_oid} has {count}. "
                "Fix: remove excess memberships, keeping only the first."
            ),
        )
        for coll_id, coll_name, max_allowed, parent_oid, count in db.query(MEMBERSHIP_COUNT_BOUNDS_QUERY)
    ]


def _find_tag_object_class_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that tags must reference objects of valid tag classes."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Invalid tag class: tag on data_id={did} references object "
                f"'{oname}' of class '{cname}' (lang_id={lid}). "
                "Valid tag classes: Data File (29), Variable (31), Timeslice (34), Scenario (35). "
                "Fix: remove the invalid tag row."
            ),
        )
        for did, oname, cname, lid in db.query(TAG_OBJECT_CLASS_QUERY, VALID_TAG_CLASS_LANG_IDS)
    ]


def _find_action_only_on_variables_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that action_id is only valid on Variable class tags/texts."""
    findings = [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Action on non-Variable tag: data_id={did}, "
                f"object '{oname}' is class '{cname}' (lang_id={lid}), not Variable. "
                "Fix: set action_id to NULL on this tag."
            ),
        )
        for did, oname, cname, lid in db.query(ACTION_TAG_FINDINGS_QUERY, (VARIABLE_CLASS_LANG_ID,))
    ]
    findings.extend(
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Action on non-Variable text: data_id={did}, "
                f"class '{cname}' (lang_id={lid}), not Variable. "
                "Fix: set action_id to NULL on this text."
            ),
        )
        for did, cname, lid in db.query(ACTION_TEXT_FINDINGS_QUERY, (VARIABLE_CLASS_LANG_ID,))
    )
    return findings


def _find_band_count_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Validate that max band_id used must not exceed t_property.max_band_id."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Band count exceeded: property '{pname}' (property_id={pid}) "
                f"has max_band_id={max_bid} but actual max band is {actual}. "
                "Fix: update max_band_id to match the actual maximum band used."
            ),
        )
        for pid, pname, max_bid, actual in db.query(BAND_COUNT_FINDINGS_QUERY)
    ]


def _find_property_values_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding] | None:
    """Find invalid property values (not implemented yet)."""
    pass


def _find_attribute_values_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding] | None:
    """Find invalid attribute values (not implemented yet)."""
    pass


def _find_case_insensitive_name_collisions_issues(
    db: SQLiteManager, /
) -> list[DatabaseValidationFinding] | None:
    """Find case-insensitive name collisions (not implemented yet)."""
    pass


def _find_custom_column_class_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding] | None:
    """Find custom column class inconsistencies (not implemented yet)."""
    pass


def find_sqlite_integrity_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Return SQLite integrity-check messages other than ``ok``."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.SQLITE,
            message=str(message),
        )
        for (message,) in db.query(SQLITE_INTEGRITY_QUERY)
        if message != "ok"
    ]


def find_foreign_key_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Return foreign-key violations reported by SQLite."""
    return [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.FOREIGN_KEYS,
            message=f"{table} rowid={rowid} violates foreign key {foreign_key_id} to {parent_table}.",
        )
        for table, rowid, parent_table, foreign_key_id in db.query(FOREIGN_KEY_CHECK_QUERY)
    ]


def find_database_relationship_issues(db: SQLiteManager, /) -> list[DatabaseValidationFinding]:
    """Return model relationship and integer-attribute findings from shared SQL."""
    findings: list[DatabaseValidationFinding] = []
    for category_value, message, class_id, object_id, attribute_id, value in db.iter_query(
        RELATIONSHIP_FINDINGS_QUERY
    ):
        category = DatabaseValidationCategory(category_value)
        if category is DatabaseValidationCategory.TYPES:
            if isinstance(value, int) or (isinstance(value, float) and value.is_integer()):
                continue
        elif not isinstance(message, str):
            raise TypeError(f"Validation SQL returned no message for category {category.value!r}.")
        findings.append(DatabaseValidationFinding(category=category, message=message))
    return findings


def repair_safe_membership_class_ids(db: SQLiteManager, /) -> None:
    """Repair membership class IDs when the object and collection agree."""
    if not db.executescript(REPAIR_MEMBERSHIP_CLASS_IDS_SCRIPT):
        raise RuntimeError("Safe membership class repairs did not complete.")


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
