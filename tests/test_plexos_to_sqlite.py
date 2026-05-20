import struct
import sqlite3
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from plexosdb import PLEXOS2SQLite, plexos_to_sqlite
from plexosdb.solution_reader import (
    _build_derived_table_map,
    _build_key_period_map,
    _coerce_value,
    _decode_bin_values,
    _phase_name,
    _read_all_bin_entries,
    _resolve_input_zip_path,
    _sanitize_name,
    _select_xml_entry,
)


def _build_test_solution_zip(path: Path) -> None:
    xml = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<MasterDataSet>
  <t_key_index>
    <key_id>100</key_id>
    <period_type_id>0</period_type_id>
    <length>2</length>
    <position>0</position>
    <period_offset>5</period_offset>
  </t_key_index>
  <t_object>
    <object_id>1</object_id>
    <name>System</name>
  </t_object>
</MasterDataSet>
"""

    values = struct.pack("<2d", 10.5, 20.5)
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("sample_solution.xml", xml)
        zf.writestr("t_data_0.BIN", values)


def _build_namespaced_solution_zip(path: Path) -> None:
    xml = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<MasterDataSet xmlns=\"http://tempuri.org/SolutionDataset.xsd\">
    <t_key_index>
        <key_id>200</key_id>
        <period_type_id>0</period_type_id>
        <length>1</length>
        <position>0</position>
        <period_offset>0</period_offset>
    </t_key_index>
    <t_object>
        <object_id>2</object_id>
        <name>SystemNS</name>
    </t_object>
</MasterDataSet>
"""
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("sample_solution.xml", xml)
        zf.writestr("t_data_0.BIN", struct.pack("<1d", 9.0))


def _build_derived_solution_zip(path: Path) -> None:
    xml = """<?xml version="1.0" encoding="utf-8"?>
<MasterDataSet>
    <t_key>
        <key_id>1</key_id>
        <phase_id>4</phase_id>
        <is_summary>0</is_summary>
        <membership_id>10</membership_id>
        <property_id>100</property_id>
        <sample_id>0</sample_id>
        <band_id>1</band_id>
    </t_key>
    <t_key>
        <key_id>2</key_id>
        <phase_id>4</phase_id>
        <is_summary>1</is_summary>
        <membership_id>10</membership_id>
        <property_id>100</property_id>
        <sample_id>0</sample_id>
        <band_id>1</band_id>
    </t_key>
    <t_key_index>
        <key_id>1</key_id>
        <period_type_id>0</period_type_id>
        <length>2</length>
        <position>0</position>
        <period_offset>0</period_offset>
    </t_key_index>
    <t_key_index>
        <key_id>2</key_id>
        <period_type_id>4</period_type_id>
        <length>2</length>
        <position>0</position>
        <period_offset>0</period_offset>
    </t_key_index>
    <t_membership>
        <membership_id>10</membership_id>
        <collection_id>20</collection_id>
        <child_object_id>1</child_object_id>
    </t_membership>
    <t_collection>
        <collection_id>20</collection_id>
        <name>Batteries</name>
    </t_collection>
    <t_property>
        <property_id>100</property_id>
        <name>Generation</name>
        <summary_name>Generation Summary</summary_name>
    </t_property>
    <t_object>
        <object_id>1</object_id>
        <name>Battery1</name>
    </t_object>
    <t_sample>
        <sample_id>0</sample_id>
        <sample_name>Mean</sample_name>
    </t_sample>
    <t_period_0>
        <interval_id>1</interval_id>
        <datetime>01/01/2012 00:00:00</datetime>
    </t_period_0>
    <t_period_0>
        <interval_id>2</interval_id>
        <datetime>01/01/2012 01:00:00</datetime>
    </t_period_0>
    <t_phase_4>
        <phase_id>4</phase_id>
        <period_id>1</period_id>
        <interval_id>1</interval_id>
    </t_phase_4>
</MasterDataSet>
"""
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("sample_solution.xml", xml)
        zf.writestr("t_data_0.BIN", struct.pack("<2d", 10.0, 20.0))
        zf.writestr("t_data_4.BIN", struct.pack("<2d", 30.0, 40.0))




def test_plexos_to_sqlite_imports_xml_and_bin(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_test_solution_zip(zip_path)

    con = plexos_to_sqlite(zip_path)
    try:
        object_name = con.execute("SELECT name FROM t_object WHERE object_id = 1").fetchone()
        assert object_name is not None
        assert object_name[0] == "System"

        rows = con.execute(
            "SELECT key_id, period_type_id, block_id, value FROM t_data_values ORDER BY block_id"
        ).fetchall()
        assert rows == [
            (100, 0, 6, 10.5),
            (100, 0, 7, 20.5),
        ]
    finally:
        con.close()


def test_plexos_to_sqlite_writes_file_db(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    sqlite_path = tmp_path / "solution.sqlite"
    _build_test_solution_zip(zip_path)

    con = plexos_to_sqlite(zip_path, sqlite_path=sqlite_path)
    con.close()

    assert sqlite_path.exists()


def test_plexos_to_sqlite_strips_xml_namespace_in_table_names(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_namespaced_solution_zip(zip_path)

    con = plexos_to_sqlite(zip_path)
    try:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "t_object" in tables
        assert "t_key_index" in tables
        assert not any(name.startswith("{") for name in tables)
    finally:
        con.close()


def test_plexos2sqlite_class_convert_and_context_manager(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_test_solution_zip(zip_path)

    client = PLEXOS2SQLite(zip_path)
    output_path = client.convert()
    assert output_path.endswith(".sqlite")

    with client as db:
        assert db.connection is not None
        count = db.connection.execute("SELECT COUNT(*) FROM t_object").fetchone()
        assert count is not None
        assert count[0] == 1


def test_plexos2sqlite_convert_requires_force_if_output_exists(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_test_solution_zip(zip_path)
    output_path = tmp_path / "out.sqlite"

    client = PLEXOS2SQLite(zip_path, output_path=output_path)
    _ = client.convert()

    client_no_force = PLEXOS2SQLite(zip_path, output_path=output_path, force=False)
    with pytest.raises(FileExistsError):
        _ = client_no_force.convert()


def test_plexos2sqlite_materializes_data_and_report_objects(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_derived_solution_zip(zip_path)

    client = PLEXOS2SQLite(zip_path, force=True)
    _ = client.convert()

    with client as db:
        con = db.connection
        assert con is not None

        data_rows = con.execute(
            'SELECT COUNT(*) FROM data."ST__Interval__Batteries__Generation"'
        ).fetchone()
        assert data_rows is not None
        assert data_rows[0] == 2

        # Rich schema: name/sample_name/band_id/datetime/value should be present
        col_names = [
            r[1]
            for r in con.execute(
                'PRAGMA data.table_info("ST__Interval__Batteries__Generation")'
            ).fetchall()
        ]
        assert "name" in col_names
        assert "sample_name" in col_names
        assert "band_id" in col_names
        assert "datetime" in col_names
        assert "value" in col_names

        # Data values should be correct
        sample = con.execute(
            'SELECT name, sample_name, band_id, value'
            ' FROM data."ST__Interval__Batteries__Generation"'
            ' ORDER BY block_id'
        ).fetchall()
        assert sample[0][0] == "Battery1"
        assert sample[0][1] == "Mean"
        assert sample[0][2] == 1
        assert sample[0][3] == 10.0

        report_rows = con.execute(
            'SELECT COUNT(*) FROM report."ST__Year__Batteries__Generation_Summary"'
        ).fetchone()
        assert report_rows is not None
        assert report_rows[0] == 2


def test_plexos_to_sqlite_missing_zip_raises(tmp_path):
    missing = tmp_path / "missing_solution.zip"
    try:
        plexos_to_sqlite(missing)
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        assert True


def test_select_xml_entry_prefers_model_name_match(tmp_path):
    zip_path = tmp_path / "run.zip"
    entries = ["random.xml", "my_model_result.xml", "other.txt"]
    selected = _select_xml_entry(zip_path, entries, model_name="model")
    assert selected == "my_model_result.xml"


def test_select_xml_entry_no_xml_raises(tmp_path):
    zip_path = tmp_path / "run.zip"
    try:
        _select_xml_entry(zip_path, ["notes.txt", "a.bin"])
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        assert True


def test_read_all_bin_entries_filters_invalid_names(tmp_path):
    zip_path = tmp_path / "mixed.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("t_data_1.BIN", b"12345678")
        zf.writestr("t_data_invalid.BIN", b"abcd")
        zf.writestr("not_data.bin", b"abcd")

    with ZipFile(zip_path, "r") as zf:
        period_data = _read_all_bin_entries(zf)

    assert set(period_data) == {1}


def test_decode_bin_values_skips_invalid_rows(tmp_path):
    xml = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<MasterDataSet>
  <t_key_index>
    <key_id>100</key_id>
    <period_type_id>0</period_type_id>
    <length>bad</length>
    <position>0</position>
    <period_offset>0</period_offset>
  </t_key_index>
  <t_key_index>
    <key_id>101</key_id>
    <period_type_id>0</period_type_id>
    <length>2</length>
    <position>100</position>
    <period_offset>0</period_offset>
  </t_key_index>
</MasterDataSet>
"""
    zip_path = tmp_path / "skip_rows.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("skip_rows.xml", xml)
        zf.writestr("t_data_0.BIN", struct.pack("<1d", 1.0))

    con = plexos_to_sqlite(zip_path)
    try:
        rows = con.execute("SELECT * FROM t_data_values").fetchall()
        assert rows == []
    finally:
        con.close()


def test_create_and_insert_rows_empty_noop():
    con = sqlite3.connect(":memory:")
    try:
        # No table should be created when rows are empty.
        from plexosdb.solution_reader import _create_and_insert_rows

        _create_and_insert_rows(con, "t_empty", [])
        table = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='t_empty'"
        ).fetchone()
        assert table is None
    finally:
        con.close()


def test_helper_value_and_name_normalization():
    assert _coerce_value(None) is None
    assert _coerce_value("   ") is None
    assert _coerce_value("12") == 12
    assert _coerce_value("12.5") == 12.5
    assert _coerce_value("abc") == "abc"

    assert _sanitize_name(None) == "Unknown"
    assert _sanitize_name("  ") == "Unknown"
    assert _sanitize_name("A---B   C") == "A_B_C"


def test_select_xml_entry_prefers_zip_stem_match(tmp_path):
    zip_path = tmp_path / "target_name.zip"
    entries = ["other.xml", "target_name.xml", "x.txt"]
    assert _select_xml_entry(zip_path, entries) == "target_name.xml"


def test_resolve_input_zip_path_variants(tmp_path):
    solution_zip = tmp_path / "one.zip"
    _build_test_solution_zip(solution_zip)

    assert _resolve_input_zip_path(solution_zip) == solution_zip

    not_zip = tmp_path / "one.txt"
    not_zip.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        _resolve_input_zip_path(not_zip)

    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        _resolve_input_zip_path(empty_dir)

    many_dir = tmp_path / "many"
    many_dir.mkdir()
    _build_test_solution_zip(many_dir / "a.zip")
    _build_test_solution_zip(many_dir / "b.zip")
    with pytest.raises(ValueError):
        _resolve_input_zip_path(many_dir)


def test_phase_name_covers_all_mappings_and_default():
    phase_ids = {
        "ST": {4},
        "MT": {3},
        "PASA": {2},
        "LT": {1},
    }
    assert _phase_name(4, phase_ids) == "ST"
    assert _phase_name(3, phase_ids) == "MT"
    assert _phase_name(2, phase_ids) == "PASA"
    assert _phase_name(1, phase_ids) == "LT"
    assert _phase_name(999, phase_ids) == "ST"


def test_build_key_period_map_uses_key_index_and_keeps_first_value():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE t_key_index (key_id TEXT, period_type_id TEXT)")
        con.executemany(
            "INSERT INTO t_key_index(key_id, period_type_id) VALUES (?, ?)",
            [("1", "0"), ("1", "4"), ("2", None)],
        )
        mapping = _build_key_period_map(
            con,
            has_key_period=False,
            key_index_cols=["key_id", "period_type_id"],
        )
        assert mapping == {1: 0, 2: None}

        no_mapping = _build_key_period_map(
            con,
            has_key_period=False,
            key_index_cols=["key_id"],
        )
        assert no_mapping == {}
    finally:
        con.close()


def test_build_derived_table_map_returns_empty_when_required_tables_missing():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE t_key (key_id TEXT)")
        assert _build_derived_table_map(con) == {}
    finally:
        con.close()


def test_decode_bin_values_returns_early_without_key_index(tmp_path):
    zip_path = tmp_path / "nobin.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("sample.xml", "<MasterDataSet></MasterDataSet>")

    con = sqlite3.connect(":memory:")
    try:
        with ZipFile(zip_path, "r") as zf:
            _decode_bin_values(con, zf)
        table = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='t_data_values'"
        ).fetchone()
        assert table is None
    finally:
        con.close()


def test_plexos2sqlite_force_overwrites_existing_file(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_test_solution_zip(zip_path)
    out_path = tmp_path / "forced.sqlite"
    out_path.write_text("not a database", encoding="utf-8")

    client = PLEXOS2SQLite(zip_path, output_path=out_path, force=True)
    out = client.convert()
    assert Path(out).exists()

    con = sqlite3.connect(out)
    try:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "t_object" in tables
    finally:
        con.close()


def test_plexos2sqlite_enter_triggers_convert_when_output_missing(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_test_solution_zip(zip_path)
    out_path = tmp_path / "auto.sqlite"
    client = PLEXOS2SQLite(zip_path, output_path=out_path, force=False)

    assert not out_path.exists()
    with client as db:
        assert out_path.exists()
        assert db.connection is not None


def test_plexos2sqlite_lazy_materialization_for_single_table(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_derived_solution_zip(zip_path)

    client = PLEXOS2SQLite(zip_path, force=True, materialize_on_enter=False)
    _ = client.convert()

    with client as db:
        con = db.connection
        assert con is not None

        with pytest.raises(sqlite3.OperationalError):
            con.execute('SELECT COUNT(*) FROM data."ST__Interval__Batteries__Generation"').fetchone()

        created = db.materialize_table("ST__Interval__Batteries__Generation", schema="data")
        assert created is True

        count = con.execute(
            'SELECT COUNT(*) FROM data."ST__Interval__Batteries__Generation"'
        ).fetchone()
        assert count is not None
        assert count[0] == 2


def test_plexos2sqlite_materialize_table_invalid_schema_and_missing_table(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_derived_solution_zip(zip_path)

    client = PLEXOS2SQLite(zip_path, force=True, materialize_on_enter=False)
    _ = client.convert()

    with client as db:
        with pytest.raises(ValueError):
            db.materialize_table("ST__Interval__Batteries__Generation", schema="invalid")

        created = db.materialize_table("DOES_NOT_EXIST", schema="data")
        assert created is False
