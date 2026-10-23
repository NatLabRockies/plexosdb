from collections.abc import Generator

import pytest

from plexosdb import DatabaseValidationCategory, DatabaseValidationError, DatabaseValidationFinding, PlexosDB
from plexosdb import checks as checks_module
from plexosdb.db_constants import PLEXOS_DEFAULT_SCHEMA


@pytest.fixture
def case_sensitive_db() -> Generator[PlexosDB, None, None]:
    db = PlexosDB()
    db.create_schema(schema=PLEXOS_DEFAULT_SCHEMA.replace("COLLATE NOCASE", "COLLATE BINARY"))
    db._db.execute("INSERT INTO t_class (class_id, name) VALUES (1, 'Generator'), (2, 'Node')")
    try:
        yield db
    finally:
        db._db.close()


@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_reports_case_collisions_without_renaming(
    case_sensitive_db: PlexosDB,
    fix_issues: bool,
) -> None:
    db = case_sensitive_db
    db._db.execute(
        "INSERT INTO t_object (object_id, class_id, name, GUID) "
        "VALUES (1, 1, 'Plant', 'a'), (2, 1, 'PLANT', 'b'), (3, 1, 'plant', 'c'), "
        "(4, 2, 'Plant', 'd')"
    )
    original_objects = db.query("SELECT * FROM t_object")
    total_changes = db._db.connection.total_changes
    finding = DatabaseValidationFinding(
        category=DatabaseValidationCategory.OBJECTS,
        message=(
            "Case-insensitive name collision in class 'Generator': "
            "'Plant' (id=1), 'PLANT' (id=2), 'plant' (id=3). "
            "Fix: rename one of the colliding objects to be unique."
        ),
    )

    assert checks_module._find_case_insensitive_name_collisions_issues(db._db) == [finding]
    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database(fix_issues=fix_issues)
    assert exc_info.value.findings == (finding,)
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_object") == original_objects


def test_name_collisions_respect_classes_and_sqlite_case_semantics(case_sensitive_db: PlexosDB) -> None:
    db = case_sensitive_db
    db._db.execute(
        "INSERT INTO t_object (object_id, class_id, name, GUID) "
        "VALUES (1, 1, 'Plant', 'a'), (2, 2, 'plant', 'b'), "
        "(3, 1, 'Other', 'c'), (4, 1, ' plant', 'd')"
    )
    assert checks_module._find_case_insensitive_name_collisions_issues(db._db) == []
    assert db.validate_database() is True


def test_name_collisions_report_each_group_and_missing_class(case_sensitive_db: PlexosDB) -> None:
    db = case_sensitive_db
    db._db.execute("PRAGMA foreign_keys = OFF")
    try:
        db._db.execute(
            "INSERT INTO t_object (object_id, class_id, name, GUID) "
            "VALUES (1, 1, 'A', 'a'), (2, 1, 'a', 'b'), "
            "(3, 99, 'B', 'c'), (4, 99, 'b', 'd')"
        )
    finally:
        db._db.execute("PRAGMA foreign_keys = ON")
    findings = checks_module._find_case_insensitive_name_collisions_issues(db._db)
    assert len(findings) == 2
    assert "class 'Generator': 'A' (id=1), 'a' (id=2)" in findings[0].message
    assert "class 'Unknown': 'B' (id=3), 'b' (id=4)" in findings[1].message
