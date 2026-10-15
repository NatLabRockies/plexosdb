from collections.abc import Generator
from pathlib import Path

import pytest

from plexosdb import ClassEnum, DatabaseValidationCategory, DatabaseValidationError, PlexosDB


@pytest.fixture
def db_with_validation_records(db_instance_with_schema: PlexosDB) -> PlexosDB:
    """Create a valid object, membership, attribute, and property graph."""
    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "Generator1", category="thermal")
    db.add_attribute(
        ClassEnum.Generator,
        "Generator1",
        attribute_name="Latitude",
        attribute_value=2.0,
    )
    db._db.execute("UPDATE t_attribute SET is_integer = 1 WHERE attribute_id = 1")
    db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", 2.0)
    return db


@pytest.fixture
def db_from_model_xml(data_folder: Path) -> Generator[PlexosDB, None, None]:
    """Load a populated PLEXOS XML model and close its database after the test."""
    db = PlexosDB.from_xml(data_folder / "run_of_river_case" / "TestSystem.xml")
    yield db
    db._db.close()


def test_validate_database_returns_true_without_mutating_valid_database(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    total_changes = db._db.connection.total_changes

    assert db.validate_database() is True
    assert db._db.connection.total_changes == total_changes


def test_validate_database_raises_with_foreign_key_findings(
    db_instance_with_schema: PlexosDB,
) -> None:
    db = db_instance_with_schema
    db._db.execute("PRAGMA foreign_keys = OFF")
    db._db.execute("INSERT INTO t_data (data_id, membership_id, property_id, value) VALUES (1, 999, 1, 2.0)")
    db._db.execute("PRAGMA foreign_keys = ON")

    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database()

    findings = [
        finding
        for finding in exc_info.value.findings
        if finding.category is DatabaseValidationCategory.FOREIGN_KEYS
    ]
    assert len(findings) == 1
    assert "t_data rowid=1" in findings[0].message
    assert "t_membership" in findings[0].message
    assert "t_data rowid=1" in str(exc_info.value)


def test_validate_database_raises_with_model_consistency_findings(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    object_id = db.get_object_id(ClassEnum.Generator, "Generator1")
    db._db.execute("UPDATE t_object SET class_id = 3 WHERE object_id = ?", (object_id,))
    db._db.execute("UPDATE t_membership SET child_class_id = 3 WHERE child_object_id = ?", (object_id,))
    db._db.execute("UPDATE t_property SET collection_id = 2 WHERE property_id = 1")
    db._db.execute(
        "UPDATE t_attribute_data SET value = 1.5 WHERE object_id = ? AND attribute_id = 1",
        (object_id,),
    )

    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database()

    findings = exc_info.value.findings
    assert {finding.category for finding in findings} == {
        DatabaseValidationCategory.OBJECTS,
        DatabaseValidationCategory.MEMBERSHIPS,
        DatabaseValidationCategory.ATTRIBUTES,
        DatabaseValidationCategory.PROPERTIES,
        DatabaseValidationCategory.TYPES,
    }
    assert any(
        "object_id=2" in finding.message
        for finding in findings
        if finding.category is DatabaseValidationCategory.OBJECTS
    )
    assert any(
        "membership_id=1" in finding.message
        for finding in findings
        if finding.category is DatabaseValidationCategory.MEMBERSHIPS
    )
    assert any(
        "object_id=2" in finding.message
        for finding in findings
        if finding.category is DatabaseValidationCategory.ATTRIBUTES
    )
    assert any(
        "data_id=1" in finding.message
        for finding in findings
        if finding.category is DatabaseValidationCategory.PROPERTIES
    )
    assert any(
        "non-integer value 1.5" in finding.message
        for finding in findings
        if finding.category is DatabaseValidationCategory.TYPES
    )


@pytest.mark.parametrize(
    "field",
    ("parent_class_id", "parent_object_id", "collection_id", "child_class_id", "child_object_id"),
)
def test_validate_database_reports_missing_membership_relations(
    db_with_validation_records: PlexosDB,
    field: str,
) -> None:
    db = db_with_validation_records
    db._db.execute(f"UPDATE t_membership SET {field} = NULL")

    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database()

    assert any(
        finding.category is DatabaseValidationCategory.MEMBERSHIPS
        and f"missing required {field}" in finding.message
        for finding in exc_info.value.findings
    )


@pytest.mark.parametrize("field", ("membership_id", "property_id"))
def test_validate_database_reports_missing_property_relations(
    db_with_validation_records: PlexosDB,
    field: str,
) -> None:
    db = db_with_validation_records
    db._db.execute(f"UPDATE t_data SET {field} = NULL")

    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database()

    assert any(
        finding.category is DatabaseValidationCategory.PROPERTIES
        and f"missing required {field}" in finding.message
        for finding in exc_info.value.findings
    )


@pytest.mark.parametrize(
    ("statement", "category"),
    (
        ("UPDATE t_object SET class_id = NULL WHERE object_id = 2", DatabaseValidationCategory.OBJECTS),
        (
            "UPDATE t_attribute SET class_id = NULL WHERE attribute_id = 1",
            DatabaseValidationCategory.ATTRIBUTES,
        ),
        (
            "UPDATE t_collection SET child_class_id = NULL WHERE collection_id = 1",
            DatabaseValidationCategory.MEMBERSHIPS,
        ),
        (
            "UPDATE t_property SET collection_id = NULL WHERE property_id = 1",
            DatabaseValidationCategory.PROPERTIES,
        ),
    ),
)
def test_validate_database_reports_missing_related_class_metadata(
    db_with_validation_records: PlexosDB,
    statement: str,
    category: DatabaseValidationCategory,
) -> None:
    db_with_validation_records._db.execute(statement)

    with pytest.raises(DatabaseValidationError) as exc_info:
        db_with_validation_records.validate_database()

    assert any(finding.category is category for finding in exc_info.value.findings)


def test_validate_database_reports_missing_required_column() -> None:
    schema = """
    CREATE TABLE t_attribute (attribute_id INTEGER, class_id INTEGER);
    CREATE TABLE t_attribute_data (object_id INTEGER, attribute_id INTEGER, value REAL);
    CREATE TABLE t_category (category_id INTEGER, class_id INTEGER);
    CREATE TABLE t_class (class_id INTEGER);
    CREATE TABLE t_collection (collection_id INTEGER, parent_class_id INTEGER, child_class_id INTEGER);
    CREATE TABLE t_data (data_id INTEGER, membership_id INTEGER, property_id INTEGER);
    CREATE TABLE t_membership (membership_id INTEGER, parent_class_id INTEGER, parent_object_id INTEGER,
                               collection_id INTEGER, child_class_id INTEGER, child_object_id INTEGER);
    CREATE TABLE t_object (object_id INTEGER, class_id INTEGER, category_id INTEGER);
    CREATE TABLE t_property (property_id INTEGER, collection_id INTEGER);
    """
    db = PlexosDB()
    try:
        db.create_schema(schema=schema)
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database()
    finally:
        db._db.close()

    assert any(
        finding.category is DatabaseValidationCategory.SCHEMA
        and "Required column 't_attribute.is_integer' is missing." in finding.message
        for finding in exc_info.value.findings
    )


def test_validate_database_reports_missing_schema_tables(db_instance: PlexosDB) -> None:
    with pytest.raises(DatabaseValidationError) as exc_info:
        db_instance.validate_database()

    assert any(
        finding.category is DatabaseValidationCategory.SCHEMA
        and "Required table 't_class' is missing." in finding.message
        for finding in exc_info.value.findings
    )


@pytest.mark.parametrize(
    ("field", "invalid_class_id", "expected_class_id"),
    (("parent_class_id", 2, 1), ("child_class_id", 3, 2)),
)
def test_validate_database_repairs_membership_class_id_when_references_agree(
    db_with_validation_records: PlexosDB,
    field: str,
    invalid_class_id: int,
    expected_class_id: int,
) -> None:
    db = db_with_validation_records
    db._db.execute(
        f"UPDATE t_membership SET {field} = ? WHERE membership_id = 1",
        (invalid_class_id,),
    )

    assert db.validate_database(fix_issues=True) is True
    assert db.query(f"SELECT {field} FROM t_membership WHERE membership_id = 1")[0][0] == expected_class_id
    assert db.validate_database() is True


def test_validate_database_rolls_back_unsafe_partial_repairs(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_membership SET parent_class_id = 2, child_class_id = 3 WHERE membership_id = 1")
    db._db.execute("UPDATE t_collection SET child_class_id = 3 WHERE collection_id = 1")

    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database(fix_issues=True)

    assert any(
        finding.category is DatabaseValidationCategory.MEMBERSHIPS for finding in exc_info.value.findings
    )
    membership_classes = db.query(
        "SELECT parent_class_id, child_class_id FROM t_membership WHERE membership_id = 1"
    )[0]
    assert membership_classes == (2, 3)


def test_validate_database_does_not_repair_memberships_with_other_findings(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_membership SET child_class_id = 3 WHERE membership_id = 1")
    db._db.execute("UPDATE t_data SET property_id = NULL WHERE data_id = 1")

    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database(fix_issues=True)

    assert {finding.category for finding in exc_info.value.findings} >= {
        DatabaseValidationCategory.MEMBERSHIPS,
        DatabaseValidationCategory.PROPERTIES,
    }
    assert db.query("SELECT child_class_id FROM t_membership WHERE membership_id = 1")[0][0] == 3


def test_validate_database_rejects_non_boolean_fix_issues(
    db_instance_with_schema: PlexosDB,
) -> None:
    with pytest.raises(TypeError, match="fix_issues must be a bool"):
        db_instance_with_schema.validate_database(fix_issues=1)  # type: ignore[arg-type]


def test_validate_database_accepts_populated_xml_model(db_from_model_xml: PlexosDB) -> None:
    assert db_from_model_xml.validate_database() is True
