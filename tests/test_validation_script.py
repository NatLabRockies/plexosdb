from pathlib import Path
import runpy
import sys

import pytest

from plexosdb import DatabaseValidationError, PlexosDB


@pytest.mark.parametrize("invalid", (False, True, "malformed_parent_key"))
@pytest.mark.parametrize("custom_output", (False, True))
def test_validation_script_writes_plain_text_report(
    db_instance_with_schema: PlexosDB,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    invalid: bool | str,
    custom_output: bool,
) -> None:
    db = db_instance_with_schema
    if invalid == "malformed_parent_key":
        db._db.execute("PRAGMA foreign_keys = OFF")
        try:
            db._db.execute("DROP TABLE t_action")
            db._db.execute("CREATE TABLE t_action (action_id INT NOT NULL, action_symbol VARCHAR(50))")
        finally:
            db._db.execute("PRAGMA foreign_keys = ON")
    elif invalid:
        db._db.execute("DROP TABLE t_tag")
    monkeypatch.chdir(tmp_path)
    report = tmp_path / ("validation.txt" if custom_output else "validation_issues.txt")
    report.write_text("Old report", encoding="utf-8")
    xml_path = tmp_path / "model.xml"

    def from_xml(cls: type[PlexosDB], path: Path) -> PlexosDB:
        assert path == xml_path
        return db

    monkeypatch.setattr(PlexosDB, "from_xml", classmethod(from_xml))
    argv = ["validate_database.py", str(xml_path)]
    if custom_output:
        argv.extend(["--output", str(report)])
    monkeypatch.setattr(sys, "argv", argv)
    script = Path(__file__).resolve().parents[1] / "examples" / "validate_database.py"
    if invalid:
        with pytest.raises(DatabaseValidationError) as exc_info:
            runpy.run_path(str(script), run_name="__main__")
        expected = "Database validation results:\n" + "".join(
            f"- [{finding.category.value}] {finding.message}\n" for finding in exc_info.value.findings
        )
        expected += f"Validation found {len(exc_info.value.findings)} errors.\n"
        if invalid == "malformed_parent_key":
            assert "[foreign_keys]" in expected
            assert "foreign key mismatch" in expected
            assert "t_action" in expected
    else:
        runpy.run_path(str(script), run_name="__main__")
        expected = "No validation issues found.\n"
    assert report.read_text(encoding="utf-8") == expected
    assert "\033" not in report.read_text(encoding="utf-8")


def test_validation_script_validates_populated_xml_model(
    data_folder: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    xml_path = data_folder / "run_of_river_case" / "TestSystem.xml"
    report = tmp_path / "validation_issues.txt"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["validate_database.py", str(xml_path)])
    script = Path(__file__).resolve().parents[1] / "examples" / "validate_database.py"

    with pytest.raises(DatabaseValidationError) as exc_info:
        runpy.run_path(str(script), run_name="__main__")

    findings = exc_info.value.findings
    assert len(findings) == 9
    assert any("Static property with tag:" in finding.message for finding in findings)
    assert any("Static property with memo:" in finding.message for finding in findings)
    assert any(
        "Duplicated static data: property 'Price' (property_id=585) "
        "on object 'Gas' (object_id=7, class='Fuel')" in finding.message
        for finding in findings
    )
    expected = "Database validation results:\n" + "".join(
        f"- [{finding.category.value}] {finding.message}\n" for finding in findings
    )
    expected += f"Validation found {len(findings)} errors.\n"
    contents = report.read_text(encoding="utf-8")
    assert contents == expected
    assert "\033" not in contents
