import pytest

from plexosdb import (
    ClassEnum,
    DatabaseValidationCategory,
    DatabaseValidationError,
    PlexosDB,
    ValidationResult,
)
from plexosdb.types import SQLiteValue
from plexosdb import checks as checks_module


@pytest.mark.parametrize(
    ("rule", "value", "valid"),
    (
        ("Between 1 And 100", 1, True),
        ("Between 1 And 100", 100, True),
        ("Between 1 And 100", 150.0, False),
        ("Between -2.5 And 1e2", -2.5, True),
        ("In (0,1)", 0, True),
        ("In (0,1)", 2, False),
        (">=1", 1, True),
        (">=1", 0, False),
        ("<=1", 1, True),
        ("<=1", 2, False),
        ("<1", 0, True),
        ("<1", 1, False),
        (">1", 2, True),
        (">1", 1, False),
        ("  >= -1e2  ", -100, True),
        ("", None, True),
        ("   ", None, True),
        (">1", None, False),
        (">1", "2", False),
        (">1", b"2", False),
    ),
)
def test_validate_value_by_rule(rule: str, value: SQLiteValue, valid: bool) -> None:
    result = PlexosDB.validate_value_by_rule(value, rule)

    assert isinstance(result, ValidationResult)
    assert result.is_valid is valid
    assert bool(result.error_message) is not valid


@pytest.mark.parametrize(
    ("rule", "message"),
    (
        ("Between 1 And 100", "Value 150.0 must be between 1.0 and 100.0"),
        ("In (0,1)", "Value 150.0 must be one of: [0.0, 1.0]"),
        (">200", "Value 150.0 must be > 200.0"),
        ("Between x And 2", "Invalid range format in rule: Between x And 2"),
        ("Between 1 And 2 And 3", "Invalid range format in rule: Between 1 And 2 And 3"),
        ("Between 1", "Invalid range format in rule: Between 1"),
        ("In ()", "Invalid set format in rule: In ()"),
        ("In (0,x)", "Invalid set format in rule: In (0,x)"),
        ("In (0,1", "Invalid set format in rule: In (0,1"),
        (">=x", "Invalid comparison format in rule: >=x"),
        ("unknown", "Unknown validation rule format: unknown"),
    ),
)
def test_validate_value_by_rule_reports_errors_consistently(rule: str, message: str) -> None:
    assert PlexosDB.validate_value_by_rule(150.0, rule) == ValidationResult(
        is_valid=False, error_message=message
    )


@pytest.mark.parametrize("fix_issues", (False, True))
@pytest.mark.parametrize("rule", (None, "", "Between 1 And 3", "In (1,2,3)", "<2", ">x", "unknown"))
def test_property_rule_validation_without_mutating(
    db_instance_with_schema: PlexosDB,
    rule: str | None,
    fix_issues: bool,
) -> None:
    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "Generator1")
    db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", 2.0)
    db._db.execute("UPDATE t_property SET validation_rule = ? WHERE property_id = 1", (rule,))
    total_changes = db._db.connection.total_changes

    if rule in ("<2", ">x", "unknown"):
        result = db.validate_value_by_rule(2.0, rule)
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert len(exc_info.value.findings) == 1
        finding = exc_info.value.findings[0]
        assert finding.category is DatabaseValidationCategory.PROPERTIES
        assert finding.message == (
            "Property value invalid: data_id=1, property 'Max Capacity' "
            f"value=2.0 fails rule '{rule}': {result.error_message}. "
            "Fix: correct the value to satisfy the validation rule."
        )
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
    assert db._db.connection.total_changes == total_changes


@pytest.mark.parametrize("fix_issues", (False, True))
@pytest.mark.parametrize("value", (None, 2.0))
@pytest.mark.parametrize("rule", (None, "", "Between 1 And 3", "In (1,2,3)", "<2", ">x", "unknown"))
def test_attribute_rule_validation_without_mutating(
    db_instance_with_schema: PlexosDB,
    rule: str | None,
    value: float | None,
    fix_issues: bool,
) -> None:
    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "Generator1")
    db.add_attribute(ClassEnum.Generator, "Generator1", attribute_name="Latitude", attribute_value=2.0)
    db._db.execute("UPDATE t_attribute SET validation_rule = ? WHERE attribute_id = 1", (rule,))
    db._db.execute("UPDATE t_attribute_data SET value = ?", (value,))
    original_data = db.query("SELECT * FROM t_attribute_data")
    total_changes = db._db.connection.total_changes

    if value is not None and rule in ("<2", ">x", "unknown"):
        result = db.validate_value_by_rule(value, rule)
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database(fix_issues=fix_issues)
        assert len(exc_info.value.findings) == 1
        finding = exc_info.value.findings[0]
        assert finding.category is DatabaseValidationCategory.ATTRIBUTES
        assert finding.message == (
            "Attribute value invalid: object 'Generator1', attribute 'Latitude' "
            f"value={value} fails rule '{rule}': {result.error_message}. "
            "Fix: correct the value to satisfy the validation rule."
        )
        assert checks_module._find_attribute_values_issues(db._db) == [finding]
    else:
        assert db.validate_database(fix_issues=fix_issues) is True
        assert checks_module._find_attribute_values_issues(db._db) == []
    assert db._db.connection.total_changes == total_changes
    assert db.query("SELECT * FROM t_attribute_data") == original_data


@pytest.mark.parametrize(
    ("class_name", "attribute_name", "value", "invalid_value"),
    (
        ("Transmission", "Loss Tolerance", 0.01, -0.01),
        ("Transmission", "Flow PTDF Threshold", 1e-6, -1e-6),
        ("Production", "Rounding Up Threshold", 0.3, 1.1),
        ("Production", "Fuel Use Function Precision", 0.001, -0.001),
        ("Performance", "MIP Relative Gap", 0.0025, -0.0025),
        ("Transmission", "Loss Function Precision", 0.01, None),
    ),
)
def test_simulation_float_attributes_override_integer_metadata(
    db_instance_with_schema: PlexosDB,
    class_name: str,
    attribute_name: str,
    value: float,
    invalid_value: float | None,
) -> None:
    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "Config")
    db.add_attribute(ClassEnum.Generator, "Config", attribute_name="Latitude", attribute_value=value)
    db._db.execute("UPDATE t_class SET name = ? WHERE class_id = 2", (class_name,))
    db._db.execute(
        "UPDATE t_attribute SET name = ?, is_integer = 1, validation_rule = NULL WHERE attribute_id = 1",
        (attribute_name,),
    )
    total_changes = db._db.connection.total_changes

    assert db.validate_database() is True
    assert db._db.connection.total_changes == total_changes
    if invalid_value is not None:
        db._db.execute("UPDATE t_attribute_data SET value = ?", (invalid_value,))
        with pytest.raises(DatabaseValidationError) as exc_info:
            db.validate_database()
        assert len(exc_info.value.findings) == 1
        assert exc_info.value.findings[0].category is DatabaseValidationCategory.ATTRIBUTES
        db._db.execute("UPDATE t_attribute SET is_integer = 0")
        with pytest.raises(DatabaseValidationError):
            db.validate_database()

    db._db.execute("UPDATE t_attribute_data SET value = ?", (value,))
    db._db.execute("UPDATE t_attribute SET validation_rule = '<0'")
    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database()
    assert any("fails rule '<0'" in finding.message for finding in exc_info.value.findings)


def test_simulation_integer_exemption_is_class_scoped(db_instance_with_schema: PlexosDB) -> None:
    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "Generator1")
    db.add_attribute(ClassEnum.Generator, "Generator1", attribute_name="Latitude", attribute_value=0.01)
    db._db.execute("UPDATE t_attribute SET name = 'Loss Tolerance', is_integer = 1")

    with pytest.raises(DatabaseValidationError) as exc_info:
        db.validate_database()
    assert any(finding.category is DatabaseValidationCategory.TYPES for finding in exc_info.value.findings)
