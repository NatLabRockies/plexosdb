import shutil
import struct
import sqlite3
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

import plexosdb.solution_reader as sr
from plexosdb.solution_reader import PlexosSolution
from plexosdb.solution_reader import (
    _build_phase_sets,
    _build_property_map,
    _build_derived_table_map,
    _build_key_period_map,
    _build_period_join,
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
    _stream_xml_to_sqlite,
)
from plexosdb.solution_reader.display import (
    _box_border,
    _box_data_line,
    _box_dots_line,
    _print_box_table,
    show_db_tables,
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


def test_plexos_solution_to_sqlite_and_context_manager(tmp_path, solution_zip):
    sol = PlexosSolution.from_zip(solution_zip)
    result = sol.to_sqlite(str(tmp_path / "solution.sqlite"), if_exists="replace", decode_bin_values=False)
    assert str(result.database).endswith(".sqlite")

    with sol:
        assert sol.connection is not None
        count = sol.connection.execute("SELECT COUNT(*) FROM t_object").fetchone()
        assert count is not None
        assert count[0] > 0


def test_plexos_solution_if_exists_fail_raises(tmp_path, solution_zip):
    output_path = tmp_path / "out.sqlite"

    sol = PlexosSolution.from_zip(solution_zip)
    sol.to_sqlite(str(output_path), if_exists="replace", decode_bin_values=False)
    sol.close()

    sol2 = PlexosSolution.from_zip(solution_zip)
    with pytest.raises(FileExistsError):
        sol2.to_sqlite(str(output_path), if_exists="fail")
    sol2.close()


def test_plexos_solution_materializes_data_and_report_objects(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    sol.materialize_table("ST__Interval__Generators__Generation", schema="data")
    con = sol.connection

    data_rows = con.execute('SELECT COUNT(*) FROM data."ST__Interval__Generators__Generation"').fetchone()
    assert data_rows is not None
    assert data_rows[0] == 35040

    # Rich schema columns should be present
    col_names = [
        r[1] for r in con.execute('PRAGMA data.table_info("ST__Interval__Generators__Generation")').fetchall()
    ]
    assert "name" in col_names
    assert "sample_name" in col_names
    assert "band_id" in col_names
    assert "datetime" in col_names
    assert "value" in col_names

    # Spot-check: first row for Coal_Gen should have expected values
    sample = con.execute(
        "SELECT name, sample_name, band_id, value"
        ' FROM data."ST__Interval__Generators__Generation"'
        " ORDER BY name, block_id"
        " LIMIT 1"
    ).fetchone()
    assert sample[0] == "Coal_Gen"
    assert sample[1] == "Mean"
    assert sample[2] == 1
    assert sample[3] == 353.0

    # Report schema
    sol.materialize_table("ST__Interval__Generators__Generation", schema="report")

    report_cols = [
        r[1]
        for r in con.execute('PRAGMA report.table_info("ST__Interval__Generators__Generation")').fetchall()
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
        ' FROM report."ST__Interval__Generators__Generation" ORDER BY timestamp LIMIT 1'
    ).fetchone()
    assert report_sample == (
        1,
        "Mean",
        "Coal_Gen",
        "-",
        "2017-01-01 00:00:00",
        1,
        353.0,
        "MW",
    )
    sol.close()


def test_stream_xml_to_sqlite_strips_namespace_in_table_names(tmp_path):
    xml = b"""<?xml version="1.0" encoding="utf-8"?>
<MasterDataSet xmlns:foo="http://example.com/">
  <foo:t_object><object_id>1</object_id><name>System</name></foo:t_object>
  <foo:t_key_index><key_id>1</key_id></foo:t_key_index>
</MasterDataSet>
"""
    con = sqlite3.connect(":memory:")
    try:
        _stream_xml_to_sqlite(con, BytesIO(xml))
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "t_object" in tables
        assert "t_key_index" in tables
        assert not any(name.startswith("{") for name in tables)
    finally:
        con.close()


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
    xml = b"""<?xml version="1.0" encoding="utf-8"?>
<MasterDataSet>
  <t_key_index>
    <key_id>100</key_id><period_type_id>0</period_type_id>
    <length>bad</length><position>0</position><period_offset>0</period_offset>
  </t_key_index>
  <t_key_index>
    <key_id>101</key_id><period_type_id>0</period_type_id>
    <length>2</length><position>100</position><period_offset>0</period_offset>
  </t_key_index>
</MasterDataSet>
"""
    zip_path = tmp_path / "skip_rows.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("skip_rows.xml", xml)
        zf.writestr("t_data_0.BIN", struct.pack("<1d", 1.0))

    con = sqlite3.connect(":memory:")
    try:
        with ZipFile(zip_path, "r") as zf:
            _stream_xml_to_sqlite(con, BytesIO(xml))
            _decode_bin_values(con, zf)
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


def test_resolve_input_zip_path_variants(tmp_path, solution_zip):
    # Direct path to an existing ZIP passes through unchanged.
    assert _resolve_input_zip_path(solution_zip) == solution_zip

    # Non-ZIP extension raises ValueError.
    not_zip = tmp_path / "one.txt"
    not_zip.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        _resolve_input_zip_path(not_zip)

    # Empty directory raises FileNotFoundError.
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        _resolve_input_zip_path(empty_dir)

    # Directory with more than one ZIP raises ValueError.
    many_dir = tmp_path / "many"
    many_dir.mkdir()
    shutil.copy(solution_zip, many_dir / "a.zip")
    shutil.copy(solution_zip, many_dir / "b.zip")
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


def test_plexos_solution_if_exists_replace(tmp_path, solution_zip):
    out_path = tmp_path / "forced.sqlite"
    out_path.write_text("not a database", encoding="utf-8")

    sol = PlexosSolution.from_zip(solution_zip)
    result = sol.to_sqlite(str(out_path), if_exists="replace", decode_bin_values=False)
    assert result.database is not None and result.database.exists()
    sol.close()

    con = sqlite3.connect(str(out_path))
    try:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "t_object" in tables
    finally:
        con.close()


def test_plexos_solution_creates_file_when_missing(tmp_path, solution_zip):
    out_path = tmp_path / "auto.sqlite"

    assert not out_path.exists()
    sol = PlexosSolution.from_zip(solution_zip)
    sol.to_sqlite(str(out_path), if_exists="reuse", decode_bin_values=False)
    assert out_path.exists()
    with sol:
        assert sol.connection is not None


def test_plexos_solution_lazy_materialization_for_single_table(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    con = sol.connection

    with pytest.raises(sqlite3.OperationalError):
        con.execute('SELECT COUNT(*) FROM data."ST__Interval__Generators__Generation"').fetchone()

    mat_result = sol.materialize_table("ST__Interval__Generators__Generation", schema="data")
    assert mat_result.created is True

    count = con.execute('SELECT COUNT(*) FROM data."ST__Interval__Generators__Generation"').fetchone()
    assert count is not None
    assert count[0] == 35040
    sol.close()


def test_plexos_solution_materialize_table_invalid_schema_and_missing_table(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)

    with pytest.raises(ValueError):
        sol.materialize_table("ST__Interval__Generators__Generation", schema="invalid")

    mat_result = sol.materialize_table("DOES_NOT_EXIST", schema="data")
    assert mat_result.created is False
    sol.close()


def test_select_xml_entry_falls_back_to_first_xml_when_no_match(tmp_path):
    zip_path = tmp_path / "model.zip"
    entries = ["zzz.xml", "aaa.xml", "readme.txt"]
    assert _select_xml_entry(zip_path, entries, model_name="nomatch") == "zzz.xml"


def test_resolve_input_zip_path_directory_with_single_zip(tmp_path, solution_zip):
    single = tmp_path / "single"
    single.mkdir()
    zip_copy = single / solution_zip.name
    shutil.copy(solution_zip, zip_copy)
    assert _resolve_input_zip_path(single) == zip_copy


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


def test_materialize_solution_tables_uses_fallback_when_meta_tables_missing(tmp_path, solution_sqlite):
    db_copy = tmp_path / "ror_copy.sqlite"
    shutil.copy(solution_sqlite, db_copy)

    sol = PlexosSolution.from_sqlite(db_copy)
    con = sol.connection
    con.execute("DROP TABLE IF EXISTS t_sample")
    con.commit()

    sr._materialize_solution_tables(con)
    count = con.execute('SELECT COUNT(*) FROM data."ST__Interval__Generators__Generation"').fetchone()[0]
    assert count > 0
    sol.close()


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


def test_client_runtime_guards_and_list_tables_validation(tmp_path, solution_zip):
    sol = PlexosSolution.from_zip(solution_zip)

    with pytest.raises(RuntimeError):
        sol.materialize_table("ST__Interval__Generators__Generation")

    with pytest.raises(RuntimeError):
        sol.list_tables()

    sol.to_sqlite(str(tmp_path / "out.sqlite"), if_exists="replace", decode_bin_values=False)

    with pytest.raises(ValueError):
        sol.list_tables(schema="invalid")

    assert "ST__Interval__Generators__Generation" in [t.name for t in sol.list_tables(schema="data")]
    assert "ST__Interval__Generators__Generation" in [t.name for t in sol.list_tables(schema="report")]
    sol.close()


def test_plexos_solution_bin_decode_recovery_from_empty_table(tmp_path):
    zip_path = tmp_path / "sample_solution.zip"
    _build_test_solution_zip(zip_path)
    out_path = tmp_path / "no_bin.sqlite"

    # Create SQLite file without BIN decoding using lower-level helpers.
    con = sqlite3.connect(str(out_path))
    with ZipFile(zip_path, "r") as zf:
        xml_entry = _select_xml_entry(zip_path, zf.namelist())
        with zf.open(xml_entry) as xml_stream:
            _stream_xml_to_sqlite(con, xml_stream)
    # Simulate stale output: t_data_values exists but is empty.
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
    con.close()

    # PlexosSolution should detect and re-decode BIN when reusing an existing file.
    sol = PlexosSolution.from_zip(zip_path)
    sol.to_sqlite(str(out_path), if_exists="reuse")
    assert sol.connection.execute("SELECT COUNT(*) FROM t_data_values").fetchone()[0] > 0
    sol.close()


def test_plexos_solution_list_tables_all_schemas(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    sol.materialize_table("ST__Interval__Generators__Generation", schema="data")
    sol.materialize_table("ST__Interval__Generators__Generation", schema="report")

    raw = [t.name for t in sol.list_tables(schema="raw")]
    assert "t_key" in raw
    assert "t_membership" in raw

    data = [t.name for t in sol.list_tables(schema="data")]
    assert "ST__Interval__Generators__Generation" in data

    report = [t.name for t in sol.list_tables(schema="report")]
    assert "ST__Interval__Generators__Generation" in report

    sol.close()


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


def test_plexos_solution_materialize_table_delegates_to_impl(solution_sqlite, monkeypatch):
    sol = PlexosSolution.from_sqlite(solution_sqlite)

    calls: list[tuple[str, str]] = []

    def _fake_materialize(_con: sqlite3.Connection, schema_name: str, table_name: str) -> bool:
        calls.append((schema_name, table_name))
        return True

    monkeypatch.setattr(sr, "_materialize_single_solution_table", _fake_materialize)
    result = sol.materialize_table("AnyTable", schema="report")
    assert result.created is True
    assert calls == [("report", "AnyTable")]
    sol.close()


def test_plexos_solution_source_property_and_pre_connect_guards(solution_zip):
    sol = PlexosSolution.from_zip(solution_zip)

    # source property is set after from_zip
    assert sol.source == solution_zip
    assert sol.name == solution_zip.stem

    # list_tables and materialize_table require an active connection
    with pytest.raises(RuntimeError):
        sol.list_tables()
    with pytest.raises(RuntimeError):
        sol.materialize_table("any_table")
    sol.close()


def test_plexos_solution_from_sqlite_opens_existing_db(solution_sqlite):
    # Re-open without the ZIP.
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    assert sol.source is None
    assert sol.name == solution_sqlite.stem
    assert sol.connection is not None

    # Derived table map is available from the raw SQL tables in the file.
    tables = [t.name for t in sol.list_tables(schema="data")]
    assert "ST__Interval__Generators__Generation" in tables

    # data/report schemas are in-memory, so materialize on demand.
    mat = sol.materialize_table("ST__Interval__Generators__Generation", schema="data")
    assert mat.created is True
    count = sol.connection.execute(
        'SELECT COUNT(*) FROM data."ST__Interval__Generators__Generation"'
    ).fetchone()
    assert count[0] == 35040

    sol.close()


def test_plexos_solution_from_sqlite_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        PlexosSolution.from_sqlite(tmp_path / "does_not_exist.sqlite")


# ---------------------------------------------------------------------------
# display.py coverage
# ---------------------------------------------------------------------------


def test_box_border_structure():
    border = _box_border([6, 8], "┌", "┬", "┐")
    assert border.startswith("┌")
    assert border.endswith("┐")
    assert "┬" in border
    assert border.count("─") == 14  # 6 + 8


def test_box_data_line_left_and_center():
    widths = [10, 12]
    left = _box_data_line(widths, ["hello", "world"])
    assert left.startswith("│")
    assert "hello" in left
    centered = _box_data_line(widths, ["hi", "there"], center=True)
    assert "hi" in centered
    assert centered.startswith("│")


def test_box_data_line_null_value():
    line = _box_data_line([10], [None])
    assert "NULL" in line


def test_box_dots_line():
    line = _box_dots_line([10, 8])
    assert line.startswith("│")
    assert line.endswith("│")
    assert "·" in line


def test_print_box_table_short_output(capsys):
    _print_box_table(["col_a", "col_b"], [("v1", "v2"), ("v3", "v4")], max_rows=20)
    out = capsys.readouterr().out
    assert "col_a" in out
    assert "v1" in out
    assert "2 rows" in out
    assert "shown" not in out


def test_print_box_table_truncation(capsys):
    rows = [(f"row_{i}", str(i)) for i in range(25)]
    _print_box_table(["name", "num"], rows, max_rows=10)
    out = capsys.readouterr().out
    assert "·" in out
    assert "25 rows" in out
    assert "10 shown" in out


def test_show_db_tables_basic(tmp_path, solution_zip, capsys):
    sol = PlexosSolution.from_zip(solution_zip)
    sol.to_sqlite(str(tmp_path / "catalog.sqlite"), if_exists="replace", decode_bin_values=False)
    show_db_tables(sol)
    out = capsys.readouterr().out
    assert "table_name" in out  # column header is always visible
    assert "rows" in out  # footer always contains row count
    sol.close()


def test_show_db_tables_truncates_with_small_max_rows(tmp_path, solution_zip, capsys):
    sol = PlexosSolution.from_zip(solution_zip)
    sol.to_sqlite(str(tmp_path / "catalog2.sqlite"), if_exists="replace", decode_bin_values=False)
    show_db_tables(sol, max_rows=4)
    out = capsys.readouterr().out
    assert "shown" in out
    sol.close()


# ---------------------------------------------------------------------------
# solution.py coverage
# ---------------------------------------------------------------------------


def test_to_sqlite_raises_when_called_on_from_sqlite_instance(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    with pytest.raises(RuntimeError, match="No ZIP path"):
        sol.to_sqlite()
    sol.close()


def test_apply_materialize_with_single_string_name(solution_sqlite):
    # _apply_materialize(str) covers the elif isinstance(materialize, str) branch
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    sol._apply_materialize("ST__Interval__Generators__Generation")
    # Table is created in the in-memory "data" schema
    result = sol.connection.execute(
        "SELECT name FROM data.sqlite_master WHERE name=?",
        ("ST__Interval__Generators__Generation",),
    ).fetchone()
    assert result is not None
    sol.close()


def test_apply_materialize_with_list_of_names(solution_sqlite):
    # _apply_materialize(list) covers the else branch (Sequence[str])
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    sol._apply_materialize(["ST__Interval__Generators__Generation"])
    result = sol.connection.execute(
        "SELECT name FROM data.sqlite_master WHERE name=?",
        ("ST__Interval__Generators__Generation",),
    ).fetchone()
    assert result is not None, "Table should be materialized from list"
    sol.close()


def test_info_returns_solution_info_from_zip(solution_zip):
    from plexosdb.solution_reader.types import SolutionInfo

    sol = PlexosSolution.from_zip(solution_zip)
    info = sol.info()
    assert isinstance(info, SolutionInfo)
    assert info.source == solution_zip
    assert info.xml_entry.endswith(".xml")
    assert info.model_name is None
    sol.close()


def test_info_with_model_name_hint(solution_zip):
    sol = PlexosSolution.from_zip(solution_zip, model_name="Base")
    info = sol.info()
    assert info.model_name == "Base"
    sol.close()


def test_info_raises_on_from_sqlite_instance(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    with pytest.raises(RuntimeError, match="No ZIP path"):
        sol.info()
    sol.close()


def test_list_tables_processed_schema(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    processed = {t.name for t in sol.list_tables(schema="processed")}
    assert {"t_class", "t_object", "t_membership", "t_property"}.issubset(processed)
    for ti in sol.list_tables(schema="processed"):
        assert ti.schema == "processed"
    sol.close()


def test_materialize_table_if_exists_fail_raises(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    sol.materialize_table("ST__Interval__Generators__Generation", schema="data")
    with pytest.raises(FileExistsError, match="already exists"):
        sol.materialize_table(
            "ST__Interval__Generators__Generation",
            schema="data",
            if_exists="fail",
        )
    sol.close()


def test_materialize_table_if_exists_replace(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    sol.materialize_table("ST__Interval__Generators__Generation", schema="data")
    result = sol.materialize_table(
        "ST__Interval__Generators__Generation",
        schema="data",
        if_exists="replace",
    )
    assert result.created is True
    sol.close()


def test_solution_name_returns_unknown_for_bare_instance():
    sol = PlexosSolution()
    assert sol.name == "unknown"


def test_ensure_bin_decoded_noop_when_zip_path_is_none(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    assert sol._zip_path is None
    sol._ensure_bin_decoded()  # should be a no-op
    sol.close()


def test_connection_property_raises_before_to_sqlite():
    sol = PlexosSolution()
    with pytest.raises(RuntimeError, match="No active connection"):
        _ = sol.connection


def test_close_is_idempotent(solution_sqlite):
    sol = PlexosSolution.from_sqlite(solution_sqlite)
    sol.close()
    sol.close()  # second call should be a no-op, not raise


def test_context_manager_enter_returns_self_and_exit_closes(tmp_path, solution_zip):
    sol = PlexosSolution.from_zip(solution_zip)
    sol.to_sqlite(str(tmp_path / "cm.sqlite"), if_exists="replace", decode_bin_values=False)
    with sol as ctx:
        assert ctx is sol
        assert ctx.connection is not None
    assert sol._connection is None


# ---------------------------------------------------------------------------
# materialize.py — uncovered branches
# ---------------------------------------------------------------------------


def test_build_period_join_returns_null_when_no_period_table_present():
    # period table exists in meta but not in the provided table_names set
    result = _build_period_join("ST__Interval__Generators__Generation", set())
    assert result == ("", "NULL AS datetime")


def test_build_period_join_returns_null_for_unknown_period_type():
    result = _build_period_join("ST__Unknown__Generators__Generation", {"t_period_0"})
    assert result == ("", "NULL AS datetime")


def test_resolve_report_unit_without_is_summary_column():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE TABLE t_key (key_id TEXT, property_id TEXT)")
        con.execute("CREATE TABLE t_property (property_id TEXT, unit_id TEXT, summary_unit_id TEXT)")
        con.execute("CREATE TABLE t_unit (unit_id TEXT, value TEXT)")
        con.execute("INSERT INTO t_key VALUES ('1', '10')")
        con.execute("INSERT INTO t_property VALUES ('10', '99', NULL)")
        con.execute("INSERT INTO t_unit VALUES ('99', 'MW')")
        unit = sr._resolve_report_unit(con, key_ids={1})
        assert unit == "MW"
    finally:
        con.close()


def test_copy_data_table_to_report_plain_mirror_when_no_rich_columns():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("ATTACH DATABASE ':memory:' AS data")
        con.execute("ATTACH DATABASE ':memory:' AS report")
        # Data table without required rich columns → plain SELECT * mirror
        con.execute('CREATE TABLE data."Plain" (key_id INTEGER, value REAL)')
        con.execute('INSERT INTO data."Plain" VALUES (1, 42.0)')
        sr._copy_data_table_to_report(con, "Plain", key_ids={1})
        row = con.execute('SELECT * FROM report."Plain"').fetchone()
        assert row == (1, 42.0)
    finally:
        con.close()


def test_copy_data_table_to_report_with_unit_text():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("ATTACH DATABASE ':memory:' AS data")
        con.execute("ATTACH DATABASE ':memory:' AS report")
        # Main schema has t_key / t_property / t_unit for unit resolution
        con.execute("CREATE TABLE t_key (key_id TEXT, property_id TEXT, is_summary TEXT)")
        con.execute("CREATE TABLE t_property (property_id TEXT, unit_id TEXT, summary_unit_id TEXT)")
        con.execute("CREATE TABLE t_unit (unit_id TEXT, value TEXT)")
        con.execute("CREATE TABLE t_object (object_id TEXT, name TEXT, category_id TEXT)")
        con.execute("CREATE TABLE t_category (category_id TEXT, name TEXT)")
        con.execute("INSERT INTO t_key VALUES ('1', '10', '0')")
        con.execute("INSERT INTO t_property VALUES ('10', '99', NULL)")
        con.execute("INSERT INTO t_unit VALUES ('99', 'GW')")
        con.execute("INSERT INTO t_object VALUES ('1', 'Gen1', '5')")
        con.execute("INSERT INTO t_category VALUES ('5', 'thermal')")
        # Data table with rich columns (band_id, sample_name, name, datetime, value)
        con.execute(
            'CREATE TABLE data."ST__Interval__Gen__Power" '
            "(band_id INT, sample_name TEXT, name TEXT, datetime TEXT, value REAL)"
        )
        con.execute(
            'INSERT INTO data."ST__Interval__Gen__Power"'
            " VALUES (1, 'Mean', 'Gen1', '2017-01-01T00:00:00', 100.0)"
        )
        sr._copy_data_table_to_report(con, "ST__Interval__Gen__Power", key_ids={1})
        row = con.execute('SELECT unit FROM report."ST__Interval__Gen__Power"').fetchone()
        assert row is not None
        assert row[0] == "GW"
    finally:
        con.close()


def test_materialize_solution_tables_fallback_when_no_meta_tables():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("ATTACH DATABASE ':memory:' AS data")
        con.execute("ATTACH DATABASE ':memory:' AS report")
        # Minimal set without t_sample / t_object / t_membership — triggers fallback sql
        con.execute(
            "CREATE TABLE t_key ("
            "key_id TEXT, phase_id TEXT, is_summary TEXT, membership_id TEXT,"
            " property_id TEXT, sample_id TEXT, band_id TEXT)"
        )
        con.execute(
            "CREATE TABLE t_key_index"
            " (key_id TEXT, period_type_id TEXT, length TEXT, position TEXT, period_offset TEXT)"
        )
        con.execute(
            "CREATE TABLE t_membership (membership_id TEXT, collection_id TEXT, child_object_id TEXT)"
        )
        con.execute("CREATE TABLE t_collection (collection_id TEXT, name TEXT)")
        con.execute(
            "CREATE TABLE t_property (property_id TEXT, name TEXT, unit_id TEXT, summary_unit_id TEXT)"
        )
        con.execute(
            "CREATE TABLE t_data_values"
            " (key_id INTEGER, period_type_id INTEGER, block_id INTEGER, value REAL)"
        )
        con.execute("INSERT INTO t_key VALUES ('1','4','0','10','100','0','1')")
        con.execute("INSERT INTO t_key_index VALUES ('1','0','1','0','0')")
        con.execute("INSERT INTO t_membership VALUES ('10','20','1')")
        con.execute("INSERT INTO t_collection VALUES ('20','Generators')")
        con.execute("INSERT INTO t_property VALUES ('100','Generation',NULL,NULL)")
        con.execute("INSERT INTO t_data_values VALUES (1,0,1,99.0)")
        con.execute("CREATE TABLE t_phase_4 (phase_id TEXT)")
        con.execute("INSERT INTO t_phase_4 VALUES ('4')")
        sr._materialize_solution_tables(con)
        # Table should be created even without metadata joins
        tables = {
            r[0] for r in con.execute("SELECT name FROM data.sqlite_master WHERE type='table'").fetchall()
        }
        assert len(tables) > 0
    finally:
        con.close()
