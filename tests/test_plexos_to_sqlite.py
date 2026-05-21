import struct
import sqlite3
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from plexosdb import PLEXOS2SQLite, plexos_to_sqlite
import plexosdb.solution_reader as sr
from plexosdb.solution_reader import (
    _build_phase_sets,
    _build_property_map,
    _build_derived_table_map,
    _build_key_period_map,
    _decode_period_rows,
    _coerce_value,
    _decode_bin_values,
    _group_key_rows_by_period,
    _period_type_name,
    _phase_name,
    _read_all_bin_entries,
    _resolve_input_zip_path,
    _sanitize_name,
    _select_xml_entry,
    _skip_bytes,
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
        <unit_id>1</unit_id>
        <summary_unit_id>1</summary_unit_id>
    </t_property>
    <t_object>
        <object_id>1</object_id>
        <name>Battery1</name>
        <category_id>10</category_id>
    </t_object>
    <t_category>
        <category_id>10</category_id>
        <name>battery-category</name>
    </t_category>
    <t_unit>
        <unit_id>1</unit_id>
        <value>MW</value>
    </t_unit>
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

        data_rows = con.execute('SELECT COUNT(*) FROM data."ST__Interval__Batteries__Generation"').fetchone()
        assert data_rows is not None
        assert data_rows[0] == 2

        # Rich schema: name/sample_name/band_id/datetime/value should be present
        col_names = [
            r[1]
            for r in con.execute('PRAGMA data.table_info("ST__Interval__Batteries__Generation")').fetchall()
        ]
        assert "name" in col_names
        assert "sample_name" in col_names
        assert "band_id" in col_names
        assert "datetime" in col_names
        assert "value" in col_names

        # Data values should be correct
        sample = con.execute(
            "SELECT name, sample_name, band_id, value"
            ' FROM data."ST__Interval__Batteries__Generation"'
            " ORDER BY block_id"
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

        report_cols = [
            r[1]
            for r in con.execute('PRAGMA report.table_info("ST__Interval__Batteries__Generation")').fetchall()
        ]
        assert report_cols == [
            "band",
            "sample_name",
            "name",
            "category",
            "timestamp",
            "interval_length",
            "Generation",
            "unit",
        ]
        report_sample = con.execute(
            'SELECT band, sample_name, name, category, timestamp, interval_length, "Generation", unit'
            ' FROM report."ST__Interval__Batteries__Generation" ORDER BY timestamp LIMIT 1'
        ).fetchone()
        assert report_sample == (
            1,
            "Mean",
            "Battery1",
            "battery-category",
            "2012-01-01 00:00:00",
            1,
            10.0,
            "MW",
        )


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
        table = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='t_empty'").fetchone()
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


def test_build_key_period_map_prefers_key_index_over_t_key_when_both_exist():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE t_key (key_id TEXT, period_type_id TEXT)")
        con.execute("CREATE TABLE t_key_index (key_id TEXT, period_type_id TEXT)")
        con.execute("INSERT INTO t_key(key_id, period_type_id) VALUES (?, ?)", ("10", "1"))
        con.execute("INSERT INTO t_key_index(key_id, period_type_id) VALUES (?, ?)", ("10", "4"))

        mapping = _build_key_period_map(
            con,
            has_key_period=True,
            key_index_cols=["key_id", "period_type_id"],
        )

        assert mapping == {10: 4}
    finally:
        con.close()


def test_build_derived_table_map_returns_empty_when_required_tables_missing():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE t_key (key_id TEXT)")
        assert _build_derived_table_map(con) == {}
    finally:
        con.close()


def test_build_derived_table_map_does_not_require_t_data_values():
    con = sqlite3.connect(":memory:")
    try:
        con.execute(
            "CREATE TABLE t_key "
            "(key_id TEXT, phase_id TEXT, is_summary TEXT, membership_id TEXT, property_id TEXT)"
        )
        con.execute("CREATE TABLE t_key_index (key_id TEXT, period_type_id TEXT, length TEXT, position TEXT)")
        con.execute("CREATE TABLE t_property (property_id TEXT, name TEXT, summary_name TEXT)")
        con.execute("CREATE TABLE t_membership (membership_id TEXT, collection_id TEXT)")
        con.execute("CREATE TABLE t_collection (collection_id TEXT, name TEXT)")
        con.execute("CREATE TABLE t_phase_4 (phase_id TEXT)")

        con.execute("INSERT INTO t_key VALUES ('1','4','0','10','100')")
        con.execute("INSERT INTO t_key_index VALUES ('1','4','1','0')")
        con.execute("INSERT INTO t_property VALUES ('100','Generation','Generation Summary')")
        con.execute("INSERT INTO t_membership VALUES ('10','20')")
        con.execute("INSERT INTO t_collection VALUES ('20','Batteries')")
        con.execute("INSERT INTO t_phase_4 VALUES ('4')")

        groups = _build_derived_table_map(con)
        assert ("data", "ST__Year__Batteries__Generation") in groups
    finally:
        con.close()


def test_build_derived_table_map_infers_summary_from_key_period_and_keeps_ampersand():
    con = sqlite3.connect(":memory:")
    try:
        con.execute(
            "CREATE TABLE t_key "
            "(key_id TEXT, phase_id TEXT, membership_id TEXT, property_id TEXT, period_type_id TEXT)"
        )
        con.execute("CREATE TABLE t_key_index (key_id TEXT, period_type_id TEXT, length TEXT, position TEXT)")
        con.execute("CREATE TABLE t_property (property_id TEXT, name TEXT, summary_name TEXT)")
        con.execute("CREATE TABLE t_membership (membership_id TEXT, collection_id TEXT)")
        con.execute("CREATE TABLE t_collection (collection_id TEXT, name TEXT)")
        con.execute("CREATE TABLE t_phase_4 (phase_id TEXT)")

        # Infer summary from key.period_type_id == 1 when explicit is_summary is missing.
        # Keep period label from key_index (4 -> Year) and keep '&' in table label.
        con.execute("INSERT INTO t_key VALUES ('1','4','10','100','1')")
        con.execute("INSERT INTO t_key_index VALUES ('1','4','1','0')")
        con.execute("INSERT INTO t_property VALUES ('100','Start & Shutdown Cost','Start & Shutdown Cost')")
        con.execute("INSERT INTO t_membership VALUES ('10','20')")
        con.execute("INSERT INTO t_collection VALUES ('20','Generators')")
        con.execute("INSERT INTO t_phase_4 VALUES ('4')")

        groups = _build_derived_table_map(con)
        assert ("data", "ST__Year__Generators__Start_&_Shutdown_Cost") in groups
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

        count = con.execute('SELECT COUNT(*) FROM data."ST__Interval__Batteries__Generation"').fetchone()
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


def test_select_xml_entry_falls_back_to_first_xml_when_no_match(tmp_path):
    zip_path = tmp_path / "model.zip"
    entries = ["zzz.xml", "aaa.xml", "readme.txt"]
    assert _select_xml_entry(zip_path, entries, model_name="nomatch") == "zzz.xml"


def test_resolve_input_zip_path_directory_with_single_zip(tmp_path):
    single = tmp_path / "single"
    single.mkdir()
    solution_zip = single / "only.zip"
    _build_test_solution_zip(solution_zip)
    assert _resolve_input_zip_path(single) == solution_zip


def test_period_type_name_none_and_unknown():
    assert _period_type_name(None) == "Period"
    assert _period_type_name(99) == "Period99"


def test_build_key_period_map_falls_back_to_t_key_when_key_index_missing_column():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE t_key (key_id TEXT, period_type_id TEXT)")
        con.execute("INSERT INTO t_key(key_id, period_type_id) VALUES ('5', '7')")
        mapping = _build_key_period_map(
            con,
            has_key_period=True,
            key_index_cols=["key_id"],
        )
        assert mapping == {5: 7}
    finally:
        con.close()


def test_build_property_map_without_summary_name_column():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE t_property (property_id TEXT, name TEXT)")
        con.execute("INSERT INTO t_property(property_id, name) VALUES ('100', 'Generation')")
        mapping = _build_property_map(con, has_summary_name=False)
        assert mapping == {100: ("Generation", "")}
    finally:
        con.close()


def test_build_phase_sets_skips_missing_id_col_and_invalid_values():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE t_phase_1 (foo TEXT)")
        con.execute("CREATE TABLE t_phase_2 (phase_id TEXT)")
        con.execute("CREATE TABLE t_phase_3 (phase_id TEXT)")
        con.execute("INSERT INTO t_phase_2(phase_id) VALUES (NULL)")
        con.execute("INSERT INTO t_phase_3(phase_id) VALUES ('bad')")

        table_names = {"t_phase_1", "t_phase_2", "t_phase_3"}
        phase_ids = _build_phase_sets(con, table_names)

        assert phase_ids["LT"] == set()
        assert phase_ids["PASA"] == set()
        assert phase_ids["MT"] == set()
        assert phase_ids["ST"] == set()
    finally:
        con.close()


def test_materialize_solution_tables_uses_fallback_when_meta_tables_missing(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_derived_solution_zip(zip_path)

    con = plexos_to_sqlite(zip_path)
    try:
        con.execute("DROP TABLE IF EXISTS t_sample")

        sr._materialize_solution_tables(con)
        rows = con.execute(
            'SELECT key_id, period_type_id, block_id, value FROM data."ST__Interval__Batteries__Generation"'
        ).fetchall()
        assert len(rows) == 2
    finally:
        con.close()


def test_materialize_solution_tables_skips_empty_group(monkeypatch):
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE t_data_values (key_id INTEGER)")
        monkeypatch.setattr(sr, "_build_derived_table_map", lambda _con: {("data", "x"): set()})
        sr._materialize_solution_tables(con)
    finally:
        con.close()


def test_bin_entry_name_map_skips_invalid_suffix(tmp_path):
    zip_path = tmp_path / "mixed.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("t_data_x.BIN", b"bad")
        zf.writestr("t_data_6.BIN", b"ok")

    with ZipFile(zip_path, "r") as zf:
        mapping = sr._bin_entry_name_map(zf)
    assert mapping == {6: "t_data_6.BIN"}


def test_skip_bytes_success_and_decode_period_rows_short_chunk(tmp_path):
    assert _skip_bytes(BytesIO(struct.pack("<2d", 1.0, 2.0)), 8) is True

    zip_path = tmp_path / "short.bin.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("t_data_0.BIN", b"1234")

    with ZipFile(zip_path, "r") as zf:
        rows = list(_decode_period_rows(zf, "t_data_0.BIN", 0, [(1, 1, 0, 0)]))
    assert rows == []


def test_group_key_rows_by_period_filters_invalid_and_non_positive_lengths():
    grouped = _group_key_rows_by_period(
        [
            ("1", "0", "0", "0", "0"),
            ("2", "x", "1", "0", "0"),
            ("3", "0", "2", "8", "1"),
        ],
        {0: "t_data_0.BIN"},
    )
    assert grouped == {0: [(3, 2, 8, 1)]}


def test_decode_bin_values_returns_early_when_key_index_empty_and_when_no_bin(tmp_path):
    zip_path = tmp_path / "empty.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("sample.xml", "<MasterDataSet></MasterDataSet>")

    con = sqlite3.connect(":memory:")
    try:
        con.execute(
            "CREATE TABLE t_key_index "
            "(key_id TEXT, period_type_id TEXT, length TEXT, position TEXT, period_offset TEXT)"
        )
        with ZipFile(zip_path, "r") as zf:
            _decode_bin_values(con, zf)

        table = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='t_data_values'"
        ).fetchone()
        assert table is None
    finally:
        con.close()


def test_client_runtime_guards_and_list_tables_validation(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_derived_solution_zip(zip_path)
    client = PLEXOS2SQLite(zip_path, force=True, materialize_on_enter=False)

    with pytest.raises(RuntimeError):
        client._ensure_data_values_decoded()

    with pytest.raises(RuntimeError):
        client.materialize_table("ST__Interval__Batteries__Generation")

    with pytest.raises(RuntimeError):
        client.list_tables()

    _ = client.convert()
    with client as db:
        with pytest.raises(ValueError):
            db.list_tables(schema="invalid")

        assert "ST__Interval__Batteries__Generation" in db.list_tables(schema="data")
        assert "ST__Interval__Batteries__Generation" in db.list_tables(schema="report")


def test_ensure_data_values_decoded_recovers_from_empty_table(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_test_solution_zip(zip_path)

    client = PLEXOS2SQLite(
        zip_path,
        force=True,
        materialize_on_enter=False,
        decode_on_convert=False,
    )
    _ = client.convert()

    with client as db:
        con = db.connection
        assert con is not None

        # Simulate stale/partial output where t_data_values exists but is empty.
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS t_data_values (
                key_id INTEGER NOT NULL,
                period_type_id INTEGER NOT NULL,
                block_id INTEGER NOT NULL,
                value REAL NOT NULL
            )
            """
        )
        con.commit()
        assert con.execute("SELECT COUNT(*) FROM t_data_values").fetchone()[0] == 0

        db._ensure_data_values_decoded()
        assert con.execute("SELECT COUNT(*) FROM t_data_values").fetchone()[0] > 0


def test_list_catalog_tables_compat_shape(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_derived_solution_zip(zip_path)
    client = PLEXOS2SQLite(zip_path, force=True, materialize_on_enter=False)
    _ = client.convert()

    with client as db:
        rows = db.list_catalog_tables()
        assert rows

        schemas = {r["table_schema"] for r in rows}
        assert {"main", "raw", "processed", "data", "report"}.issubset(schemas)

        by_schema = {}
        for row in rows:
            by_schema.setdefault(row["table_schema"], set()).add(row["table_name"])

        assert "plexos2sqlite" in by_schema["main"]
        assert "classes" in by_schema["raw"]
        assert "classes" in by_schema["processed"]
        assert "ST__Interval__Batteries__Generation" in by_schema["data"]
        assert "ST__Interval__Batteries__Generation" in by_schema["report"]


def test_table_label_part_and_report_interval_length_edges():
    assert sr._table_label_part(None) == "Unknown"
    assert sr._report_interval_length("SinglePart") is None


def test_resolve_report_unit_guard_paths_and_no_row():
    con = sqlite3.connect(":memory:")
    try:
        assert sr._resolve_report_unit(con, key_ids=set()) is None
        assert sr._resolve_report_unit(con, key_ids={1}) is None

        con.execute("CREATE TABLE t_key (key_id TEXT, property_id TEXT)")
        con.execute("CREATE TABLE t_property (property_id TEXT, unit_id TEXT, summary_unit_id TEXT)")
        con.execute("CREATE TABLE t_unit (unit_id TEXT, value TEXT)")

        # Exercises the no-is_summary SQL expression path and the no-row return.
        assert sr._resolve_report_unit(con, key_ids={999}) is None
    finally:
        con.close()


def test_copy_data_table_to_report_fallback_with_null_unit():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("ATTACH DATABASE ':memory:' AS data")
        con.execute("ATTACH DATABASE ':memory:' AS report")
        con.execute('CREATE TABLE data."NoRichCols" (key_id INTEGER, value REAL)')
        con.execute('INSERT INTO data."NoRichCols" (key_id, value) VALUES (1, 42.0)')

        sr._copy_data_table_to_report(con, "NoRichCols", key_ids={1})

        rows = con.execute('SELECT key_id, value FROM report."NoRichCols"').fetchall()
        assert rows == [(1, 42.0)]
    finally:
        con.close()


def test_materialize_single_solution_table_paths(monkeypatch):
    con = sqlite3.connect(":memory:")
    copied: list[tuple[str, set[int]]] = []
    try:
        monkeypatch.setattr(sr, "_build_derived_table_map", lambda _con: {})
        assert sr._materialize_single_solution_table(con, "data", "T") is False

        monkeypatch.setattr(sr, "_build_derived_table_map", lambda _con: {("data", "T"): {1}})
        monkeypatch.setattr(sr, "_ensure_join_indexes", lambda _con, _tables: None)
        monkeypatch.setattr(
            sr,
            "_build_fallback_create_sql",
            lambda _schema, _table, _ids: (
                'CREATE TABLE data."T" AS '
                "SELECT 1 AS key_id, 1 AS period_type_id, 1 AS block_id, 2.0 AS value"
            ),
        )
        monkeypatch.setattr(
            sr,
            "_copy_data_table_to_report",
            lambda _con, table_name, *, key_ids: copied.append((table_name, set(key_ids))),
        )

        assert sr._materialize_single_solution_table(con, "report", "T") is True
        assert sr._materialize_single_solution_table(con, "data", "T") is True
        assert copied == [("T", {1}), ("T", {1})]
    finally:
        con.close()


def test_materialize_single_solution_table_from_subset_early_returns(tmp_path, monkeypatch):
    con = sqlite3.connect(":memory:")
    zip_path = tmp_path / "empty.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("x.txt", "x")

    try:
        with ZipFile(zip_path, "r") as zf:
            monkeypatch.setattr(sr, "_build_derived_table_map", lambda _con: {})
            assert (
                sr._materialize_single_solution_table_from_subset(
                    con,
                    table_name="T",
                    schema_name="data",
                    key_rows=[(1, 0, 1, 0, 0)],
                    zf=zf,
                )
                is False
            )

            monkeypatch.setattr(sr, "_build_derived_table_map", lambda _con: {("data", "T"): {1}})
            monkeypatch.setattr(sr, "_bin_entry_name_map", lambda _zf: {})
            assert (
                sr._materialize_single_solution_table_from_subset(
                    con,
                    table_name="T",
                    schema_name="data",
                    key_rows=[(1, 0, 1, 0, 0)],
                    zf=zf,
                )
                is False
            )

            monkeypatch.setattr(sr, "_bin_entry_name_map", lambda _zf: {0: "t_data_0.BIN"})
            monkeypatch.setattr(sr, "_group_key_rows_by_period", lambda _rows, _entries: {})
            assert (
                sr._materialize_single_solution_table_from_subset(
                    con,
                    table_name="T",
                    schema_name="data",
                    key_rows=[(1, 0, 1, 0, 0)],
                    zf=zf,
                )
                is False
            )
    finally:
        con.close()


def test_materialize_single_solution_table_from_subset_skips_missing_period_entry(tmp_path, monkeypatch):
    con = sqlite3.connect(":memory:")
    zip_path = tmp_path / "empty.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("x.txt", "x")

    try:
        monkeypatch.setattr(sr, "_build_derived_table_map", lambda _con: {("data", "T"): {1}})
        monkeypatch.setattr(sr, "_bin_entry_name_map", lambda _zf: {0: "t_data_0.BIN"})
        monkeypatch.setattr(sr, "_group_key_rows_by_period", lambda _rows, _entries: {1: [(1, 1, 0, 0)]})
        monkeypatch.setattr(sr, "_decode_period_rows", lambda *_args, **_kwargs: iter(()))
        monkeypatch.setattr(sr, "_ensure_join_indexes", lambda _con, _tables: None)
        monkeypatch.setattr(
            sr,
            "_build_fallback_create_sql",
            lambda _schema,
            _table,
            _ids,
            dv_source="main.t_data_values": f'CREATE TABLE data."T" AS SELECT * FROM {dv_source}',
        )
        monkeypatch.setattr(sr, "_copy_data_table_to_report", lambda *_args, **_kwargs: None)

        with ZipFile(zip_path, "r") as zf:
            assert (
                sr._materialize_single_solution_table_from_subset(
                    con,
                    table_name="T",
                    schema_name="data",
                    key_rows=[(1, 0, 1, 0, 0)],
                    zf=zf,
                )
                is True
            )
            rows = con.execute('SELECT COUNT(*) FROM data."T"').fetchone()[0]
            assert rows == 0
    finally:
        con.close()


def test_decode_period_rows_seek_exception_and_skip_progress():
    class FakeStream:
        def __init__(self, payload: bytes) -> None:
            self._stream = BytesIO(payload)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, n: int) -> bytes:
            return self._stream.read(n)

        def seek(self, _pos: int) -> int:
            raise OSError("seek unsupported")

    class FakeZip:
        def __init__(self, payload: bytes) -> None:
            self.payload = payload

        def open(self, _entry_name: str, _mode: str):
            return FakeStream(self.payload)

    rows = list(
        _decode_period_rows(
            FakeZip(struct.pack("<3d", 1.0, 2.0, 3.0)),
            "ignored.BIN",
            0,
            [(10, 1, 8, 0)],
        )
    )
    assert rows == [(10, 0, 1, 2.0)]

    # Second row overlaps previous bytes; seek() raises and row is skipped.
    skipped_rows = list(
        _decode_period_rows(
            FakeZip(struct.pack("<3d", 1.0, 2.0, 3.0)),
            "ignored.BIN",
            0,
            [(1, 2, 0, 0), (2, 1, 8, 0)],
        )
    )
    assert skipped_rows == [(1, 0, 1, 1.0), (1, 0, 2, 2.0)]


def test_decode_bin_values_no_period_entries_and_no_grouped_rows(tmp_path):
    con = sqlite3.connect(":memory:")
    try:
        con.execute(
            "CREATE TABLE t_key_index ("
            "key_id TEXT, period_type_id TEXT, length TEXT, position TEXT, period_offset TEXT"
            ")"
        )
        con.execute("INSERT INTO t_key_index VALUES ('1', '0', '2', '0', '0')")

        zip_no_bin = tmp_path / "nobin.zip"
        with ZipFile(zip_no_bin, "w", compression=ZIP_DEFLATED) as zf:
            zf.writestr("sample.xml", "<MasterDataSet></MasterDataSet>")

        with ZipFile(zip_no_bin, "r") as zf:
            _decode_bin_values(con, zf)

        table = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='t_data_values'"
        ).fetchone()
        assert table is None

        zip_with_bin = tmp_path / "withbin.zip"
        with ZipFile(zip_with_bin, "w", compression=ZIP_DEFLATED) as zf:
            zf.writestr("t_data_0.BIN", struct.pack("<1d", 5.0))

        con.execute("DELETE FROM t_key_index")
        con.execute("INSERT INTO t_key_index VALUES ('1', '0', '0', '0', '0')")

        with ZipFile(zip_with_bin, "r") as zf:
            _decode_bin_values(con, zf)

        row_count = con.execute("SELECT COUNT(*) FROM t_data_values").fetchone()[0]
        assert row_count == 0
    finally:
        con.close()


def test_materialize_table_full_data_and_empty_key_rows_paths(tmp_path, monkeypatch):
    zip_path = tmp_path / "sample_solution.zip"
    _build_derived_solution_zip(zip_path)
    client = PLEXOS2SQLite(zip_path, force=True, materialize_on_enter=False)
    _ = client.convert()

    with client as db:
        con = db.connection
        assert con is not None

        # No full data table and no key_index rows for selected keys.
        con.execute("DELETE FROM t_key_index")
        monkeypatch.setattr(sr, "_build_derived_table_map", lambda _con: {("data", "AnyTable"): {1}})
        assert db.materialize_table("AnyTable", schema="data") is False

        # Full data path delegates to _materialize_single_solution_table.
        con.execute(
            "CREATE TABLE IF NOT EXISTS t_data_values ("
            "key_id INTEGER, period_type_id INTEGER, block_id INTEGER, value REAL"
            ")"
        )
        con.execute("DELETE FROM t_data_values")
        con.execute("INSERT INTO t_data_values VALUES (1, 0, 1, 1.0)")

        calls: list[tuple[str, str]] = []

        def _fake_materialize(_con: sqlite3.Connection, schema_name: str, table_name: str) -> bool:
            calls.append((schema_name, table_name))
            return True

        monkeypatch.setattr(sr, "_materialize_single_solution_table", _fake_materialize)
        assert db.materialize_table("AnotherTable", schema="report") is True
        assert calls == [("report", "AnotherTable")]


def test_timestamp_block_names_and_list_catalog_runtime_guards(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_test_solution_zip(zip_path)
    client = PLEXOS2SQLite(zip_path, force=True, materialize_on_enter=False)

    assert client._timestamp_block_names() == []
    with pytest.raises(RuntimeError):
        client.list_catalog_tables()
