import pytest

from plexosdb import (
    ClassEnum,
    DatabaseValidationCategory,
    DatabaseValidationError,
    PlexosDB,
    ValidationResult,
)
from plexosdb.types import SQLiteValue


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
