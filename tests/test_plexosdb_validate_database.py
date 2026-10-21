from collections.abc import Generator
from pathlib import Path

import pytest

from plexosdb import ClassEnum, DatabaseValidationCategory, DatabaseValidationError, PlexosDB
from plexosdb import checks as checks_module
from plexosdb.exceptions import DatabaseValidationFinding


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


def test_find_category_class_issues_accepts_matching_categories(
    db_with_validation_records: PlexosDB,
) -> None:
    assert checks_module._find_category_class_issues(db_with_validation_records._db) == []


def test_find_attribute_class_issues_accepts_matching_classes(
    db_with_validation_records: PlexosDB,
) -> None:
    assert checks_module._find_attribute_class_issues(db_with_validation_records._db) == []


@pytest.mark.parametrize("column_class_id", (2, 3, None))
@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_checks_custom_column_class_without_updating(
    db_with_validation_records: PlexosDB,
    column_class_id: int | None,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute(
        "INSERT INTO t_custom_column (column_id, class_id, name) VALUES (1, ?, 'Notes')",
        (column_class_id,),
    )
    db._db.execute("INSERT INTO t_memo_object (object_id, column_id, value) VALUES (2, 1, 'memo')")
    original_columns = db.query("SELECT * FROM t_custom_column")
    original_memos = db.query("SELECT * FROM t_memo_object")
    total_changes = db._db.connection.total_changes
    expected_findings = (
        [
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.OBJECTS,
                message=(
                    "Custom column class mismatch: object 'Generator1' (class_id=2) "
                    "has custom column 'Notes' (class_id=3). "
                    "Fix: update the custom column's class_id to 2."
                ),
            ),
        ]
        if column_class_id == 3
        else []
    )

    assert checks_module._find_custom_column_class_issues(db._db) == expected_findings
    if expected_findings:
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert exc_info.value.findings == tuple(expected_findings)
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_custom_column") == original_columns
    assert db.query("SELECT * FROM t_memo_object") == original_memos


def test_find_custom_column_class_issues_ignores_unassigned_columns(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    db._db.execute("INSERT INTO t_custom_column (column_id, class_id, name) VALUES (1, 3, 'Notes')")

    assert checks_module._find_custom_column_class_issues(db._db) == []
    assert db.validate_database() is True


@pytest.mark.parametrize(
    ("max_band_id", "bands", "actual_max"),
    (
        (1, (), None),
        (None, (5,), None),
        (1, (None,), None),
        (2, (1,), None),
        (2, (1, 2), None),
        (1, (1, 3, 2), 3),
        (0, (1,), 1),
        (2, (None, 3), 3),
    ),
)
@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_checks_band_count_without_updating(
    db_with_validation_records: PlexosDB,
    max_band_id: int | None,
    bands: tuple[int | None, ...],
    actual_max: int | None,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET max_band_id = ? WHERE property_id = 1", (max_band_id,))
    for data_id, band_id in enumerate(bands, start=1):
        if data_id > 1:
            db._db.execute(
                "INSERT INTO t_data (data_id, membership_id, property_id, value) VALUES (?, 1, 1, ?)",
                (data_id, float(data_id + 1)),
            )
        db._db.execute("INSERT INTO t_band (data_id, band_id) VALUES (?, ?)", (data_id, band_id))
    original_properties = db.query("SELECT * FROM t_property")
    original_bands = db.query("SELECT * FROM t_band")
    total_changes = db._db.connection.total_changes
    expected_findings = (
        [
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.PROPERTIES,
                message=(
                    "Band count exceeded: property 'Max Capacity' (property_id=1) "
                    f"has max_band_id={max_band_id} but actual max band is {actual_max}. "
                    "Fix: update max_band_id to match the actual maximum band used."
                ),
            ),
        ]
        if actual_max is not None
        else []
    )

    assert checks_module._find_band_count_issues(db._db) == expected_findings
    if expected_findings:
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert exc_info.value.findings == tuple(expected_findings)
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_property") == original_properties
    assert db.query("SELECT * FROM t_band") == original_bands


def test_find_band_count_issues_groups_by_property(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    db.add_property(ClassEnum.Generator, "Generator1", "Max Energy", 3.0)
    db._db.execute("UPDATE t_property SET max_band_id = 1 WHERE property_id = 1")
    db._db.execute("UPDATE t_property SET max_band_id = 5 WHERE property_id = 2")
    db._db.execute("INSERT INTO t_band (data_id, band_id) SELECT data_id, property_id + 2 FROM t_data")

    findings = checks_module._find_band_count_issues(db._db)
    assert len(findings) == 1
    assert "property 'Max Capacity' (property_id=1)" in findings[0].message
    assert "actual max band is 3" in findings[0].message


@pytest.mark.parametrize("lang_id", (29, 31, 34, 35, None, 0, 2, 99))
@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_checks_tag_object_class_without_deleting(
    db_with_validation_records: PlexosDB,
    lang_id: int | None,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET is_dynamic = 1 WHERE property_id = 1")
    db._db.execute("UPDATE t_class SET lang_id = ? WHERE class_id = 2", (lang_id,))
    db._db.execute("INSERT INTO t_tag (data_id, object_id) VALUES (1, 2)")
    original_tags = db.query("SELECT * FROM t_tag")
    total_changes = db._db.connection.total_changes
    expected_findings = (
        [
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.PROPERTIES,
                message=(
                    "Invalid tag class: tag on data_id=1 references object "
                    f"'Generator1' of class 'Generator' (lang_id={lang_id}). "
                    "Valid tag classes: Data File (29), Variable (31), Timeslice (34), Scenario (35). "
                    "Fix: remove the invalid tag row."
                ),
            ),
        ]
        if lang_id in (0, 2, 99)
        else []
    )

    assert checks_module._find_tag_object_class_issues(db._db) == expected_findings
    if expected_findings:
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert exc_info.value.findings == tuple(expected_findings)
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_tag") == original_tags


def test_find_tag_object_class_issues_accepts_no_tags(
    db_with_validation_records: PlexosDB,
) -> None:
    assert checks_module._find_tag_object_class_issues(db_with_validation_records._db) == []


@pytest.mark.parametrize("lang_id", (29, 31, 34, 35, None))
@pytest.mark.parametrize("action_id", (None, 0, 1))
@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_checks_actions_only_on_variables_without_mutating(
    db_with_validation_records: PlexosDB,
    lang_id: int | None,
    action_id: int | None,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET is_dynamic = 1 WHERE property_id = 1")
    db._db.execute("UPDATE t_class SET lang_id = ? WHERE class_id = 2", (lang_id,))
    db._db.execute("INSERT INTO t_action (action_id) VALUES (0), (1)")
    db._db.execute("INSERT INTO t_tag (data_id, object_id, action_id) VALUES (1, 2, ?)", (action_id,))
    db._db.execute("INSERT INTO t_text (data_id, class_id, action_id) VALUES (1, 2, ?)", (action_id,))
    original_tags = db.query("SELECT * FROM t_tag")
    original_texts = db.query("SELECT * FROM t_text")
    total_changes = db._db.connection.total_changes
    expected_findings = []
    if action_id is not None and lang_id in (29, 34, 35):
        expected_findings = [
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.PROPERTIES,
                message=(
                    "Action on non-Variable tag: data_id=1, "
                    f"object 'Generator1' is class 'Generator' (lang_id={lang_id}), not Variable. "
                    "Fix: set action_id to NULL on this tag."
                ),
            ),
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.PROPERTIES,
                message=(
                    "Action on non-Variable text: data_id=1, "
                    f"class 'Generator' (lang_id={lang_id}), not Variable. "
                    "Fix: set action_id to NULL on this text."
                ),
            ),
        ]

    assert checks_module._find_action_only_on_variables_issues(db._db) == expected_findings
    if expected_findings:
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert exc_info.value.findings == tuple(expected_findings)
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_tag") == original_tags
    assert db.query("SELECT * FROM t_text") == original_texts


@pytest.mark.parametrize(
    ("max_count", "is_one_to_many", "max_allowed"),
    (
        (-1, 0, None),
        (-1, 1, None),
        (-1, None, None),
        (0, 1, 0),
        (1, 1, 1),
        (2, 0, None),
        (3, 0, None),
        (None, 0, 1),
        (None, 1, None),
        (None, None, None),
        (-2, 0, 1),
        (-2, 1, None),
        (-2, None, 1),
    ),
)
@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_checks_membership_count_bounds_without_removing(
    db_with_validation_records: PlexosDB,
    max_count: int | None,
    is_one_to_many: int | None,
    max_allowed: int | None,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db.add_object(ClassEnum.Generator, "Generator2")
    db._db.execute(
        "UPDATE t_collection SET max_count = ?, is_one_to_many = ? WHERE collection_id = 1",
        (max_count, is_one_to_many),
    )
    original_memberships = db.query("SELECT * FROM t_membership")
    total_changes = db._db.connection.total_changes
    expected_findings = (
        [
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.MEMBERSHIPS,
                message=(
                    "Membership count exceeded: collection 'Generators' "
                    f"(collection_id=1) allows max {max_allowed}, "
                    "but parent_object_id=1 has 2. "
                    "Fix: remove excess memberships, keeping only the first."
                ),
            ),
        ]
        if max_allowed is not None
        else []
    )

    assert checks_module._find_membership_count_bounds_issues(db._db) == expected_findings
    if expected_findings:
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert exc_info.value.findings == tuple(expected_findings)
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_membership") == original_memberships


def test_find_membership_count_bounds_issues_groups_by_parent_and_collection(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    child_id = db.add_object(ClassEnum.Generator, "Generator2")
    db._db.execute("DELETE FROM t_membership WHERE child_object_id = ?", (child_id,))
    db._db.execute("UPDATE t_collection SET max_count = 1")
    db._db.execute(
        "INSERT INTO t_membership "
        "(parent_class_id, parent_object_id, collection_id, child_class_id, child_object_id) "
        "VALUES (1, 2, 1, 2, 3), (1, 1, 2, 3, 3)"
    )

    assert checks_module._find_membership_count_bounds_issues(db._db) == []
    db._db.execute(
        "INSERT INTO t_membership "
        "(parent_class_id, parent_object_id, collection_id, child_class_id, child_object_id) "
        "VALUES (1, 2, 1, 2, 2)"
    )
    findings = checks_module._find_membership_count_bounds_issues(db._db)
    assert len(findings) == 1
    assert "collection_id=1" in findings[0].message
    assert "parent_object_id=2 has 2" in findings[0].message


@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_reports_missing_system_membership_without_creating(
    db_with_validation_records: PlexosDB,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_class SET lang_id = 1 WHERE class_id = 1")
    object_id = db.add_object(ClassEnum.Generator, "Generator2")
    db._db.execute("DELETE FROM t_membership WHERE child_object_id = ?", (object_id,))
    original_memberships = db.query("SELECT * FROM t_membership")
    total_changes = db._db.connection.total_changes
    finding = DatabaseValidationFinding(
        category=DatabaseValidationCategory.MEMBERSHIPS,
        message=(
            f"Missing system membership: Object 'Generator2' (object_id={object_id}) "
            "has no system membership. "
            "Fix: create a system membership with the correct collection for this class."
        ),
    )

    assert checks_module._find_system_membership_existence_issues(db._db) == [finding]
    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database(fix_issues=fix_issues)
    assert exc_info.value.findings == (finding,)
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_membership") == original_memberships


def test_find_system_membership_existence_issues_skips_missing_system_class(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    db.add_object(ClassEnum.Generator, "Generator2")
    db._db.execute("DELETE FROM t_membership WHERE child_object_id = 3")
    db._db.execute("UPDATE t_class SET lang_id = NULL")

    assert checks_module._find_system_membership_existence_issues(db._db) == []


def test_find_system_membership_existence_issues_accepts_memberships_and_exempts_system_object(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_class SET lang_id = 1 WHERE class_id = 1")

    assert checks_module._find_system_membership_existence_issues(db._db) == []
    assert db.validate_database() is True


@pytest.mark.parametrize("child_object_id", (None, 1))
def test_find_system_membership_existence_issues_uses_lang_id_and_ignores_unrelated_children(
    db_with_validation_records: PlexosDB,
    child_object_id: int | None,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_class SET lang_id = 1 WHERE class_id = 3")
    db._db.execute(
        "INSERT INTO t_membership (membership_id, parent_class_id, child_object_id) VALUES (99, 3, ?)",
        (child_object_id,),
    )
    findings = checks_module._find_system_membership_existence_issues(db._db)

    assert len(findings) == 1
    assert "Object 'Generator1' (object_id=2)" in findings[0].message
    db._db.execute("UPDATE t_membership SET child_object_id = 2 WHERE membership_id = 99")
    assert checks_module._find_system_membership_existence_issues(db._db) == []


@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_reports_attribute_class_mismatch_without_deleting(
    db_with_validation_records: PlexosDB,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_attribute SET class_id = 3 WHERE attribute_id = 1")
    original_data = db.query("SELECT * FROM t_attribute_data")
    total_changes = db._db.connection.total_changes
    finding = DatabaseValidationFinding(
        category=DatabaseValidationCategory.ATTRIBUTES,
        message=(
            "Attribute-class mismatch: attribute 'Latitude' (class_id=3) "
            "on object 'Generator1' (class_id=2). "
            "Fix: remove the invalid attribute_data row."
        ),
    )

    assert checks_module._find_attribute_class_issues(db._db) == [finding]
    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database(fix_issues=fix_issues)
    assert exc_info.value.findings == (finding,)
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_attribute_data") == original_data


@pytest.mark.parametrize("table", ("t_attribute", "t_object"))
def test_validate_database_preserves_missing_attribute_class_findings(
    db_with_validation_records: PlexosDB,
    table: str,
) -> None:
    db = db_with_validation_records
    db._db.execute(f"UPDATE {table} SET class_id = NULL")

    assert checks_module._find_attribute_class_issues(db._db) == []
    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database()
    assert any(
        finding.category is DatabaseValidationCategory.ATTRIBUTES and "NULL" in finding.message
        for finding in exc_info.value.findings
    )


def test_find_property_collection_mismatch_issues_accepts_matching_collections(
    db_with_validation_records: PlexosDB,
) -> None:
    assert checks_module._find_property_collection_mismatch_issues(db_with_validation_records._db) == []


def test_find_static_property_artifacts_issues_accepts_no_artifacts(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET is_dynamic = 0 WHERE property_id = 1")

    assert checks_module._find_static_property_artifacts_issues(db._db) == []


@pytest.mark.parametrize(
    ("table", "artifact_type", "extra_columns", "extra_values"),
    (
        ("t_tag", "tag", ", object_id", ", 1"),
        ("t_text", "text", ", class_id", ", 1"),
        ("t_date_from", "date_from", "", ""),
        ("t_date_to", "date_to", "", ""),
        ("t_memo_data", "memo", "", ""),
    ),
)
@pytest.mark.parametrize("is_dynamic", (0, 1, None))
@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_checks_static_property_artifacts_without_mutating(
    db_with_validation_records: PlexosDB,
    table: str,
    artifact_type: str,
    extra_columns: str,
    extra_values: str,
    is_dynamic: int | None,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET is_dynamic = ? WHERE property_id = 1", (is_dynamic,))
    db._db.execute(
        "INSERT INTO t_data (data_id, membership_id, property_id, value) "
        "SELECT 2, membership_id, property_id, 3.0 FROM t_data WHERE data_id = 1"
    )
    db._db.execute("INSERT INTO t_band (data_id, band_id) VALUES (2, 2)")
    db._db.execute(f"INSERT INTO {table} (data_id{extra_columns}) SELECT data_id{extra_values} FROM t_data")
    original_artifacts = db.query(f"SELECT * FROM {table}")
    total_changes = db._db.connection.total_changes
    expected_findings = (
        [
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.PROPERTIES,
                message=(
                    f"Static property with {artifact_type}: 'Max Capacity' (property_id=1) "
                    f"is static but has 2 {table} row(s). "
                    f"Fix: set is_dynamic=1 on this property, or remove the {table} rows."
                ),
            ),
        ]
        if is_dynamic == 0
        else []
    )

    assert checks_module._find_static_property_artifacts_issues(db._db) == expected_findings
    if expected_findings:
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert exc_info.value.findings == tuple(expected_findings)
    else:
        assert db.validate_database(fix_issues=fix_issues) is True

    assert db._db.connection.total_changes == total_changes
    assert db.query(f"SELECT * FROM {table}") == original_artifacts
    assert db.query("SELECT is_dynamic FROM t_property WHERE property_id = 1") == [(is_dynamic,)]


@pytest.mark.parametrize(
    ("bands", "expected_band"),
    (
        ((), 1),
        (((2, 1),), 1),
        (((1, None), (2, 1)), 1),
        (((1, 3), (2, 3)), 3),
        (((2, 2),), None),
    ),
)
@pytest.mark.parametrize("is_dynamic", (0, 1, None))
@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_checks_duplicate_static_data_without_deleting(
    db_with_validation_records: PlexosDB,
    bands: tuple[tuple[int, int | None], ...],
    expected_band: int | None,
    is_dynamic: int | None,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET is_dynamic = ? WHERE property_id = 1", (is_dynamic,))
    db._db.execute(
        "INSERT INTO t_data (data_id, membership_id, property_id, value) "
        "SELECT 2, membership_id, property_id, value + 1 FROM t_data WHERE data_id = 1"
    )
    for data_id, band_id in bands:
        db._db.execute("INSERT INTO t_band (data_id, band_id) VALUES (?, ?)", (data_id, band_id))
    original_data = db.query("SELECT * FROM t_data")
    original_bands = db.query("SELECT * FROM t_band")
    total_changes = db._db.connection.total_changes
    expected_findings = (
        [
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.PROPERTIES,
                message=(
                    "Duplicated static data: membership_id=1, property_id=1, "
                    f"band_id={expected_band}, count=2. "
                    "Fix: remove duplicate data rows, keeping only the last."
                ),
            ),
        ]
        if is_dynamic == 0 and expected_band is not None
        else []
    )

    assert checks_module._find_duplicate_static_data_issues(db._db) == expected_findings
    if expected_findings:
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert exc_info.value.findings == tuple(expected_findings)
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_data") == original_data
    assert db.query("SELECT * FROM t_band") == original_bands


def test_find_duplicate_static_data_issues_accepts_distinct_memberships_and_properties(
    db_with_validation_records: PlexosDB,
) -> None:
    db = db_with_validation_records
    db.add_object(ClassEnum.Generator, "Generator2")
    db.add_property(ClassEnum.Generator, "Generator2", "Max Capacity", 2.0)
    db.add_property(ClassEnum.Generator, "Generator1", "Max Energy", 2.0)
    db._db.execute("UPDATE t_property SET is_dynamic = 0")

    assert checks_module._find_duplicate_static_data_issues(db._db) == []
    assert db.validate_database() is True


@pytest.fixture
def db_with_matching_data_graphs(db_with_validation_records: PlexosDB) -> PlexosDB:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET is_dynamic = 1 WHERE property_id = 1")
    db._db.execute(
        "INSERT INTO t_data (data_id, membership_id, property_id, value) "
        "SELECT 2, membership_id, property_id, value FROM t_data WHERE data_id = 1"
    )
    return db


@pytest.mark.parametrize("fix_issues", (False, True))
@pytest.mark.parametrize("is_dynamic", (0, 1, None))
def test_validate_database_reports_duplicate_data_graphs_without_deleting(
    db_with_matching_data_graphs: PlexosDB,
    fix_issues: bool,
    is_dynamic: int | None,
) -> None:
    db = db_with_matching_data_graphs
    db._db.execute("UPDATE t_property SET is_dynamic = ? WHERE property_id = 1", (is_dynamic,))
    original_data = db.query("SELECT * FROM t_data")
    total_changes = db._db.connection.total_changes
    finding = DatabaseValidationFinding(
        category=DatabaseValidationCategory.PROPERTIES,
        message=(
            "Duplicated data graph: 2 identical data rows (data_ids=[1, 2]) "
            "for membership_id=1, property_id=1. Fix: remove the duplicate data rows."
        ),
    )

    assert checks_module._find_duplicate_data_graphs_issues(db._db) == [finding]
    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database(fix_issues=fix_issues)
    assert exc_info.value.findings == (
        *checks_module._find_duplicate_static_data_issues(db._db),
        finding,
    )
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_data") == original_data


@pytest.mark.parametrize(
    ("uids", "duplicate_counts"),
    (
        ((None, None, None), ()),
        ((0, 1, 2), ()),
        ((None, 1, 2), ()),
        ((0, 0, None), ((0, 2),)),
        ((123, 123, 123), ((123, 3),)),
        ((5, 5, 9, 9, None), ((5, 2), (9, 2))),
    ),
)
@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_checks_duplicate_uids_without_reassigning(
    db_with_validation_records: PlexosDB,
    uids: tuple[int | None, ...],
    duplicate_counts: tuple[tuple[int, int], ...],
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET is_dynamic = 1 WHERE property_id = 1")
    db._db.execute("UPDATE t_data SET uid = ? WHERE data_id = 1", (uids[0],))
    for data_id, uid in enumerate(uids[1:], start=2):
        db._db.execute(
            "INSERT INTO t_data (data_id, membership_id, property_id, value, uid) VALUES (?, 1, 1, ?, ?)",
            (data_id, float(data_id + 1), uid),
        )
    original_data = db.query("SELECT * FROM t_data")
    total_changes = db._db.connection.total_changes
    expected_findings = [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Duplicated UID: uid={uid} appears {count} times in t_data. "
                "Fix: assign new unique UIDs to the duplicate rows."
            ),
        )
        for uid, count in duplicate_counts
    ]

    assert checks_module._find_duplicate_uids_issues(db._db) == expected_findings
    if expected_findings:
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert exc_info.value.findings == tuple(expected_findings)
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_data") == original_data


@pytest.mark.parametrize(
    ("table", "label", "extra_columns", "extra_values"),
    (
        ("t_tag", "tag", ", object_id", ", 1"),
        ("t_text", "text", ", class_id", ", 1"),
        ("t_date_from", "date_from", "", ""),
        ("t_date_to", "date_to", "", ""),
        ("t_band", "band", "", ""),
        ("t_memo_data", "memo", "", ""),
    ),
)
@pytest.mark.parametrize("orphan_count", (0, 1, 10, 12))
@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_reports_orphaned_child_rows_without_deleting(
    db_with_validation_records: PlexosDB,
    table: str,
    label: str,
    extra_columns: str,
    extra_values: str,
    orphan_count: int,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET is_dynamic = 1 WHERE property_id = 1")
    db._db.execute(f"INSERT INTO {table} (data_id{extra_columns}) VALUES (1{extra_values})")
    db._db.execute("PRAGMA foreign_keys = OFF")
    try:
        for data_id in reversed(range(100, 100 + orphan_count)):
            db._db.execute(
                f"INSERT INTO {table} (data_id{extra_columns}) VALUES (?{extra_values})", (data_id,)
            )
    finally:
        db._db.execute("PRAGMA foreign_keys = ON")
    original_rows = db.query(f"SELECT * FROM {table}")
    total_changes = db._db.connection.total_changes
    expected_findings = []
    if orphan_count:
        sample = list(range(100, 100 + min(orphan_count, 10)))
        more = f" (+{orphan_count - 10} more)" if orphan_count > 10 else ""
        expected_findings.append(
            DatabaseValidationFinding(
                category=DatabaseValidationCategory.PROPERTIES,
                message=(
                    f"Orphaned {label} rows: {orphan_count} row(s) in {table} "
                    f"reference non-existent data_ids {sample}{more}. "
                    f"Fix: DELETE FROM {table} WHERE data_id NOT IN (SELECT data_id FROM t_data)."
                ),
            )
        )

    assert checks_module._find_orphaned_child_rows_issues(db._db) == expected_findings
    if expected_findings:
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert [
            finding
            for finding in exc_info.value.findings
            if finding.category is DatabaseValidationCategory.PROPERTIES
        ] == expected_findings
        assert (
            sum(
                finding.category is DatabaseValidationCategory.FOREIGN_KEYS
                for finding in exc_info.value.findings
            )
            == orphan_count
        )
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
    assert db._db.connection.total_changes == total_changes
    assert db.query(f"SELECT * FROM {table}") == original_rows


@pytest.mark.parametrize(
    ("table", "label", "column"),
    (("t_tag", "tag", "object_id"), ("t_text", "text", "class_id")),
)
def test_find_orphaned_child_rows_issues_counts_rows_not_distinct_data_ids(
    db_with_validation_records: PlexosDB,
    table: str,
    label: str,
    column: str,
) -> None:
    db = db_with_validation_records
    db._db.execute(f"INSERT INTO {table} (data_id, {column}) VALUES (1, 1), (1, 2)")
    db._db.execute("PRAGMA foreign_keys = OFF")
    try:
        db._db.execute("DELETE FROM t_data WHERE data_id = 1")
    finally:
        db._db.execute("PRAGMA foreign_keys = ON")

    assert checks_module._find_orphaned_child_rows_issues(db._db) == [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Orphaned {label} rows: 2 row(s) in {table} "
                "reference non-existent data_ids [1, 1]. "
                f"Fix: DELETE FROM {table} WHERE data_id NOT IN (SELECT data_id FROM t_data)."
            ),
        )
    ]


@pytest.mark.parametrize(
    "statement",
    (
        "UPDATE t_data SET value = 3 WHERE data_id = 2",
        "UPDATE t_data SET property_id = 2 WHERE data_id = 2",
        "UPDATE t_data SET membership_id = NULL WHERE data_id = 2",
        "INSERT INTO t_band (data_id, band_id) VALUES (2, 2)",
        "INSERT INTO t_band (data_id, band_id) VALUES (2, NULL)",
        "INSERT INTO t_tag (data_id, object_id) VALUES (1, 1), (2, 2)",
        "INSERT INTO t_tag (data_id, object_id, action_id) VALUES (1, 1, NULL), (2, 1, 1)",
        "INSERT INTO t_tag (data_id, object_id) VALUES (2, 1)",
        "INSERT INTO t_text (data_id, class_id, value) VALUES (1, 1, 'a'), (2, 2, 'a')",
        "INSERT INTO t_text (data_id, class_id, value) VALUES (1, 1, 'a'), (2, 1, 'b')",
        "INSERT INTO t_text (data_id, class_id, action_id) VALUES (1, 1, NULL), (2, 1, 1)",
        "INSERT INTO t_text (data_id, class_id) VALUES (2, 1)",
        "INSERT INTO t_date_from (data_id, date) VALUES (2, '2026-01-01')",
        "INSERT INTO t_date_to (data_id, date) VALUES (2, '2026-01-02')",
        "INSERT INTO t_memo_data (data_id, value) VALUES (2, 'memo')",
    ),
)
def test_find_duplicate_data_graphs_issues_distinguishes_each_graph_field(
    db_with_matching_data_graphs: PlexosDB,
    statement: str,
) -> None:
    db = db_with_matching_data_graphs
    db._db.execute("INSERT INTO t_action (action_id) VALUES (1)")
    db._db.execute(statement)

    assert checks_module._find_duplicate_data_graphs_issues(db._db) == []


def test_find_duplicate_data_graphs_issues_matches_unordered_full_graphs(
    db_with_matching_data_graphs: PlexosDB,
) -> None:
    db = db_with_matching_data_graphs
    db._db.execute("INSERT INTO t_action (action_id) VALUES (0), (1)")
    db._db.execute(
        "INSERT INTO t_tag (data_id, object_id, action_id) "
        "VALUES (1, 1, NULL), (1, 2, 1), (2, 2, 1), (2, 1, 0)"
    )
    db._db.execute(
        "INSERT INTO t_text (data_id, class_id, value, action_id) "
        "VALUES (1, 1, 'a', NULL), (1, 2, 'b', 1), (2, 2, 'b', 1), (2, 1, 'a', 0)"
    )
    db._db.execute("INSERT INTO t_band (data_id, band_id) VALUES (2, 1)")
    for table, column, value in (
        ("t_date_from", "date", "2026-01-01"),
        ("t_date_to", "date", "2026-01-02"),
        ("t_memo_data", "value", "memo"),
    ):
        db._db.execute(f"INSERT INTO {table} (data_id, {column}) SELECT data_id, ? FROM t_data", (value,))

    findings = checks_module._find_duplicate_data_graphs_issues(db._db)
    assert len(findings) == 1
    assert "data_ids=[1, 2]" in findings[0].message


def test_find_duplicate_data_graphs_issues_groups_all_matching_rows(
    db_with_matching_data_graphs: PlexosDB,
) -> None:
    db = db_with_matching_data_graphs
    db._db.execute(
        "INSERT INTO t_data (data_id, membership_id, property_id, value, uid, state) "
        "VALUES (3, 1, 1, 2.0, 100, 1), (4, 1, 1, NULL, 101, 0), (5, 1, 1, NULL, 102, 1)"
    )
    db._db.execute("INSERT INTO t_memo_data (data_id, value) VALUES (1, NULL)")
    findings = checks_module._find_duplicate_data_graphs_issues(db._db)

    assert [finding.message for finding in findings] == [
        "Duplicated data graph: 3 identical data rows (data_ids=[1, 2, 3]) "
        "for membership_id=1, property_id=1. Fix: remove the duplicate data rows.",
        "Duplicated data graph: 2 identical data rows (data_ids=[4, 5]) "
        "for membership_id=1, property_id=1. Fix: remove the duplicate data rows.",
    ]


@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_reports_property_collection_mismatch_without_deleting(
    db_with_validation_records: PlexosDB,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    db._db.execute("UPDATE t_property SET collection_id = 2 WHERE property_id = 1")
    original_data = db.query("SELECT * FROM t_data")
    total_changes = db._db.connection.total_changes
    expected_finding = DatabaseValidationFinding(
        category=DatabaseValidationCategory.PROPERTIES,
        message=(
            "Property-collection mismatch: data_id=1, "
            "property 'Max Capacity' collection_id=2 != membership collection_id=1. "
            "Fix: remove the invalid data row."
        ),
    )

    assert checks_module._find_property_collection_mismatch_issues(db._db) == [expected_finding]
    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database(fix_issues=fix_issues)

    assert exc_info.value.findings == (expected_finding,)
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_data") == original_data


@pytest.mark.parametrize("table", ("t_property", "t_membership"))
def test_validate_database_preserves_missing_collection_findings(
    db_with_validation_records: PlexosDB,
    table: str,
) -> None:
    db = db_with_validation_records
    db._db.execute(f"UPDATE {table} SET collection_id = NULL")

    assert checks_module._find_property_collection_mismatch_issues(db._db) == []
    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database()

    assert any(
        finding.category is DatabaseValidationCategory.PROPERTIES
        and "t_data.data_id=1" in finding.message
        and "NULL" in finding.message
        for finding in exc_info.value.findings
    )


@pytest.mark.parametrize("fix_issues", (False, True))
def test_validate_database_reports_category_class_mismatch_without_repairing(
    db_with_validation_records: PlexosDB,
    fix_issues: bool,
) -> None:
    db = db_with_validation_records
    object_id = db.get_object_id(ClassEnum.Generator, "Generator1")
    node_class_id = db.get_class_id(ClassEnum.Node)
    category_id = db.add_category(ClassEnum.Node, "nodes")
    db._db.execute("UPDATE t_object SET category_id = ? WHERE object_id = ?", (category_id, object_id))
    total_changes = db._db.connection.total_changes

    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database(fix_issues=fix_issues)

    assert exc_info.value.findings == (
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.OBJECTS,
            message=(
                f"Category mismatch: Object 'Generator1' (object_id={object_id}) "
                f"has class_id=2 but category 'nodes' has class_id={node_class_id}. "
                "Fix: reset category to the default '-' category for this class."
            ),
        ),
    )
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT category_id FROM t_object WHERE object_id = ?", (object_id,)) == [(category_id,)]


@pytest.mark.parametrize(
    "finder_name",
    (
        "_find_sqlite_integrity_issues",
        "_find_database_schema_issues",
        "_find_foreign_key_issues",
        "_find_database_relationship_issues",
        "_find_category_class_issues",
        "_find_property_collection_mismatch_issues",
        "_find_static_property_artifacts_issues",
        "_find_duplicate_static_data_issues",
        "_find_duplicate_data_graphs_issues",
        "_find_duplicate_uids_issues",
        "_find_orphaned_child_rows_issues",
        "_find_attribute_class_issues",
        "_find_system_membership_existence_issues",
        "_find_membership_count_bounds_issues",
        "_find_tag_object_class_issues",
        "_find_action_only_on_variables_issues",
        "_find_band_count_issues",
        "_find_property_values_issues",
        "_find_attribute_values_issues",
        "_find_case_insensitive_name_collisions_issues",
        "_find_custom_column_class_issues",
    ),
)
def test_validate_database_collects_each_model_check(
    db_with_validation_records: PlexosDB,
    monkeypatch: pytest.MonkeyPatch,
    finder_name: str,
) -> None:
    db = db_with_validation_records
    finding = DatabaseValidationFinding(category=DatabaseValidationCategory.OBJECTS, message=finder_name)

    def find_issues(manager: object) -> list[DatabaseValidationFinding]:
        assert manager is db._db
        return [finding]

    monkeypatch.setattr(checks_module, finder_name, find_issues)

    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database()

    assert exc_info.value.findings == (finding,)


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
        "Attribute-class mismatch: attribute 'Latitude' (class_id=2) "
        "on object 'Generator1' (class_id=3)." in finding.message
        for finding in findings
        if finding.category is DatabaseValidationCategory.ATTRIBUTES
    )
    assert any(
        "data_id=1" in finding.message
        for finding in findings
        if finding.category is DatabaseValidationCategory.PROPERTIES
    )
    assert any(
        "class='Node'" in finding.message
        and "class_id=3" in finding.message
        and "object='Generator1'" in finding.message
        and "object_id=2" in finding.message
        and "property='Latitude'" in finding.message
        and "attribute_id=1" in finding.message
        and "non-integer value 1.5" in finding.message
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


def test_validate_database_reports_static_property_issues_in_populated_xml_model(
    db_from_model_xml: PlexosDB,
) -> None:
    total_changes = db_from_model_xml._db.connection.total_changes

    with pytest.raises(DatabaseValidationError) as exc_info:
        db_from_model_xml.validate_database()

    expected_findings = [
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                f"Static property with {artifact_type}: '{name}' (property_id={pid}) "
                f"is static but has {count} {table} row(s). "
                f"Fix: set is_dynamic=1 on this property, or remove the {table} rows."
            ),
        )
        for artifact_type, table, pid, name, count in (
            ("tag", "t_tag", 52, "Units", 1),
            ("tag", "t_tag", 585, "Price", 3),
            ("tag", "t_tag", 2121, "Flow Coefficient", 2),
            ("tag", "t_tag", 4934, "Sense", 1),
            ("tag", "t_tag", 4949, "RHS", 1),
            ("memo", "t_memo_data", 2035, "Max Flow", 1),
            ("memo", "t_memo_data", 2043, "Resistance", 1),
            ("memo", "t_memo_data", 2044, "Reactance", 1),
        )
    ]
    expected_findings.append(
        DatabaseValidationFinding(
            category=DatabaseValidationCategory.PROPERTIES,
            message=(
                "Duplicated static data: membership_id=6, property_id=585, band_id=1, count=3. "
                "Fix: remove duplicate data rows, keeping only the last."
            ),
        )
    )
    assert exc_info.value.findings == tuple(expected_findings)
    assert db_from_model_xml._db.connection.total_changes == total_changes
