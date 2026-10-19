"""XML import preserves text; the database schema owns numeric conversion."""

import sqlite3
import struct
import xml.etree.ElementTree as ET
from contextlib import closing
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import pytest

from plexosdb import PlexosDB, XMLHandler, XMLRecord
from plexosdb.enums import Schema
from plexosdb.solution_reader import PlexosSolution

TEXT_VALUES = [
    "0,7",
    "0, 7",
    "(1, 2)",
    "[1, 2]",
    "{'key': [1, 2j]}",
    "{1, 2}",
    "'quoted'",
    '"quoted"',
    "None",
    "True",
    "true",
    "FALSE",
    "false",
    "b'bytes'",
    "000123",
    "113_316_1",
    "7706j",
    "7999j",
    "1_0+2j",
    "0x10",
    "0x10000000000000000",
    "(42)",
    "9223372036854775807",
    "-9223372036854775808",
    "9223372036854775808",
    "11339885002100928821",
    "-9223372036854775809",
    "(9223372036854775808)",
    "NaN",
    "nan",
    "inf",
    "-Infinity",
    "1e999",
    "1.0000000000000002",
    " 001.00 ",
    "  text  ",
    " ",
    "a & b < c",
    "électricité",
]


@pytest.mark.parametrize("in_memory", [True, False])
@pytest.mark.parametrize("value", [*TEXT_VALUES, None])
def test_xml_records_preserve_raw_values(tmp_path: Path, value: str | None, in_memory: bool) -> None:
    root = ET.Element("MasterDataSet")
    row = ET.SubElement(root, "t_text")
    ET.SubElement(row, "data_id").text = "0001"
    ET.SubElement(row, "value").text = value
    source = tmp_path / "source.xml"
    ET.ElementTree(root).write(source, encoding="utf-8")

    handler = XMLHandler.parse(source, in_memory=in_memory)
    records: list[XMLRecord] = handler.get_records(Schema.Text, rename_dict={"data_id": "record_id"})
    assert records == [{"record_id": "0001", "value": value}]


@pytest.mark.parametrize("value", TEXT_VALUES)
def test_every_model_text_column_round_trips(tmp_path: Path, value: str) -> None:
    with closing(sqlite3.connect(":memory:")) as connection:
        schema = PlexosDB(new_db=True, fpath_or_conn=connection)
        schema.create_schema(version=None)
        text_columns: dict[str, list[str]] = {}
        root = ET.Element("MasterDataSet")
        for table in Schema:
            columns = schema.query("SELECT name, type FROM pragma_table_info(?)", (table.name,))
            row = ET.SubElement(root, table.name)
            text_columns[table.name] = []
            for name, kind in columns:
                is_text = "CHAR" in kind or "TEXT" in kind or "CLOB" in kind
                ET.SubElement(row, name).text = value if is_text else "1"
                if is_text:
                    text_columns[table.name].append(name)

    source = tmp_path / "source.xml"
    target = tmp_path / "export.xml"
    ET.ElementTree(root).write(source, encoding="utf-8")
    for path in (source, target):
        with closing(sqlite3.connect(":memory:")) as connection:
            db = PlexosDB.from_xml(path, fpath_or_conn=connection)
            for table, columns in text_columns.items():
                for column in columns:
                    assert db.query(f'SELECT "{column}", typeof("{column}") FROM "{table}"') == [
                        (value, "text")
                    ], (table, column, value)
            if path == source:
                db.to_xml(target)
                exported = ET.parse(target)
                for table, columns in text_columns.items():
                    for column in columns:
                        assert exported.findtext(f".//{{*}}{table}/{{*}}{column}") == value


@pytest.mark.parametrize("value", TEXT_VALUES)
def test_solution_xml_text_columns_preserve_spelling(tmp_path: Path, value: str) -> None:
    root = ET.Element("MasterDataSet")
    row = ET.SubElement(root, "t_text")
    ET.SubElement(row, "data_id").text = "1"
    ET.SubElement(row, "value").text = value
    archive = tmp_path / "solution.zip"
    with ZipFile(archive, "w") as zipped:
        zipped.writestr("solution.xml", ET.tostring(root))
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite(decode_bin_values=False)
        assert solution.connection.execute("SELECT value, typeof(value) FROM t_text").fetchall() == [
            (value, "text")
        ]


@pytest.mark.parametrize(
    "value, expected",
    [("000123", 123.0), ("-0.5", -0.5), ("1e-20", 1e-20), ("1.0000000000000002", 1.0000000000000002)],
)
def test_numeric_model_columns_use_schema_affinity(tmp_path: Path, value: str, expected: float) -> None:
    source = tmp_path / "source.xml"
    source.write_text(
        f"<MasterDataSet><t_data><data_id>0001</data_id><value>{value}</value></t_data></MasterDataSet>",
        encoding="utf-8",
    )
    target = tmp_path / "export.xml"
    for path in (source, target):
        with closing(sqlite3.connect(":memory:")) as connection:
            db = PlexosDB.from_xml(path, fpath_or_conn=connection)
            assert db.query("SELECT data_id, typeof(data_id), value, typeof(value) FROM t_data") == [
                (1, "integer", expected, "real")
            ]
            if path == source:
                db.to_xml(target)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("true", 1),
        ("TRUE", 1),
        ("True", 1),
        ("false", 0),
        ("FALSE", 0),
        ("False", 0),
        ("1", 1),
        ("0", 0),
        ("  TRUE  ", 1),
        ("\tFalse\n", 0),
    ],
)
def test_boolean_conversion_is_limited_to_bit_columns(tmp_path: Path, value: str, expected: int) -> None:
    source = tmp_path / "source.xml"
    source.write_text(
        "<MasterDataSet><t_class><class_id>1</class_id>"
        f"<name>{value}</name><is_enabled>{value}</is_enabled></t_class></MasterDataSet>",
        encoding="utf-8",
    )
    target = tmp_path / "export.xml"
    for path in (source, target):
        with closing(sqlite3.connect(":memory:")) as connection:
            db = PlexosDB.from_xml(path, fpath_or_conn=connection)
            assert db.query("SELECT name, is_enabled, typeof(is_enabled) FROM t_class") == [
                (value, expected, "integer")
            ]
            if path == source:
                db.to_xml(target)


@pytest.mark.parametrize(
    "value, expected, storage",
    [
        ("9223372036854775807", 9223372036854775807, "integer"),
        ("-9223372036854775808", -9223372036854775808, "integer"),
        ("9223372036854775808", float(9223372036854775808), "real"),
        ("11339885002100928821", float(11339885002100928821), "real"),
        ("-9223372036854775809", float(-9223372036854775809), "real"),
        ("0x10000000000000000", "0x10000000000000000", "text"),
        ("(9223372036854775808)", "(9223372036854775808)", "text"),
        ("NaN", "NaN", "text"),
        ("inf", "inf", "text"),
    ],
)
def test_numeric_columns_follow_sqlite_integer_range(
    tmp_path: Path, value: str, expected: int | float | str, storage: str
) -> None:
    """SQLite may round oversized integers to REAL; text columns remain lossless."""
    source = tmp_path / "source.xml"
    source.write_text(
        f"<MasterDataSet><t_data><data_id>1</data_id><uid>{value}</uid></t_data></MasterDataSet>",
        encoding="utf-8",
    )
    with closing(sqlite3.connect(":memory:")) as connection:
        db = PlexosDB.from_xml(source, fpath_or_conn=connection)
        assert db.query("SELECT uid, typeof(uid) FROM t_data") == [(expected, storage)]


@pytest.mark.parametrize("empty_value", ["", "<value />"])
def test_empty_and_missing_xml_values_remain_null(tmp_path: Path, empty_value: str) -> None:
    source = tmp_path / "source.xml"
    source.write_text(
        "<MasterDataSet><t_text><data_id>1</data_id><class_id>1</class_id>"
        f"{empty_value}</t_text></MasterDataSet>",
        encoding="utf-8",
    )
    target = tmp_path / "export.xml"
    for path in (source, target):
        with closing(sqlite3.connect(":memory:")) as connection:
            db = PlexosDB.from_xml(path, fpath_or_conn=connection)
            assert db.query("SELECT value FROM t_text") == [(None,)]
            if path == source:
                db.to_xml(target)


def test_numeric_looking_object_names_remain_distinct(tmp_path: Path) -> None:
    names = [
        "000123",
        "123",
        "0,7",
        "0.7",
        "113_316_1",
        "1133161",
        "7706j",
        "7999j",
        "true",
        "1",
        "'quoted'",
        "quoted",
    ]
    root = ET.Element("MasterDataSet")
    cls = ET.SubElement(root, "t_class")
    ET.SubElement(cls, "class_id").text = "2"
    ET.SubElement(cls, "name").text = "Generator"
    for object_id, name in enumerate(names, start=1):
        row = ET.SubElement(root, "t_object")
        ET.SubElement(row, "object_id").text = str(object_id)
        ET.SubElement(row, "GUID").text = f"00000000-0000-0000-0000-{object_id:012d}"
        ET.SubElement(row, "class_id").text = "2"
        ET.SubElement(row, "name").text = name
    source = tmp_path / "source.xml"
    target = tmp_path / "export.xml"
    ET.ElementTree(root).write(source, encoding="utf-8")
    for path in (source, target):
        with closing(sqlite3.connect(":memory:")) as connection:
            db = PlexosDB.from_xml(path, fpath_or_conn=connection)
            assert set(db.list_objects_by_class("Generator")) == set(names)
            for object_id, name in enumerate(names, start=1):
                assert db.get_object_id("Generator", name) == object_id
            if path == source:
                db.to_xml(target)


@pytest.mark.parametrize("key_id", ["000100", " 100 "])
@pytest.mark.parametrize("materialize", ["all", "single"])
@pytest.mark.parametrize("date_format", ["%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S"])
@pytest.mark.parametrize("padding", ["", " \t\n"])
def test_solution_materialization_matches_numeric_ids(
    tmp_path: Path, key_id: str, materialize: str, date_format: str, padding: str
) -> None:
    dates = [padding + datetime(2026, 1, 1, hour).strftime(date_format) + padding for hour in (0, 1)]
    rows: list[tuple[str, XMLRecord]] = [
        (
            "t_key_index",
            {"key_id": key_id, "period_type_id": "0", "length": "2", "position": "0", "period_offset": "0"},
        ),
        (
            "t_key",
            {
                "key_id": key_id,
                "membership_id": "0010",
                "property_id": "0020",
                "sample_id": "0030",
                "band_id": "01",
                "phase_id": "4",
                "is_summary": "0",
            },
        ),
        ("t_membership", {"membership_id": "10", "child_object_id": "0040", "collection_id": "0050"}),
        ("t_object", {"object_id": "40", "name": "000123", "category_id": "0060"}),
        ("t_category", {"category_id": "60", "name": "None"}),
        ("t_collection", {"collection_id": "50", "name": "Generators"}),
        (
            "t_property",
            {"property_id": "20", "name": "Generation", "unit_id": "0070", "summary_unit_id": "0070"},
        ),
        ("t_unit", {"unit_id": "70", "value": "MW"}),
        ("t_sample", {"sample_id": "30", "sample_name": "Mean"}),
        ("t_period_0", {"interval_id": "0001", "datetime": dates[0]}),
        ("t_period_0", {"interval_id": " 2 ", "datetime": dates[1]}),
    ]
    root = ET.Element("MasterDataSet")
    for table, record in rows:
        row = ET.SubElement(root, table)
        for column, value in record.items():
            ET.SubElement(row, column).text = value
    archive = tmp_path / "solution.zip"
    with ZipFile(archive, "w") as zipped:
        zipped.writestr("solution.xml", ET.tostring(root))
        zipped.writestr("t_data_0.BIN", struct.pack("<2d", 10.5, 20.5))

    table = '"ST__Interval__Generators__Generation"'
    database = tmp_path / "solution.sqlite"
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite(database, materialize="all" if materialize == "all" else "none")
        if materialize == "single":
            assert solution.materialize_table("ST__Interval__Generators__Generation").created
        assert solution.connection.execute("SELECT key_id FROM t_key").fetchall() == [(key_id,)]
        assert solution.connection.execute(
            f"SELECT name, sample_name, band_id, datetime, value FROM data.{table} ORDER BY block_id"
        ).fetchall() == [
            ("000123", "Mean", 1, dates[0], 10.5),
            ("000123", "Mean", 1, dates[1], 20.5),
        ]
        assert solution.connection.execute(
            f"SELECT name, category, unit, Generation FROM report.{table} ORDER BY timestamp"
        ).fetchall() == [("000123", "None", "MW", 10.5), ("000123", "None", "MW", 20.5)]
        assert solution.connection.execute(
            f"SELECT timestamp FROM report.{table} ORDER BY timestamp"
        ).fetchall() == [("2026-01-01 00:00:00",), ("2026-01-01 01:00:00",)]
    with PlexosSolution.from_sqlite(database) as solution:
        assert solution.materialize_table("ST__Interval__Generators__Generation").created
        assert solution.connection.execute(
            f"SELECT timestamp FROM report.{table} ORDER BY timestamp"
        ).fetchall() == [("2026-01-01 00:00:00",), ("2026-01-01 01:00:00",)]


@pytest.mark.parametrize("offset, expected", [(None, 0), ("", 0), (" \t\n", 0), ("\u00a0", 0), (" 3 ", 3)])
def test_optional_bin_offset_preserves_raw_text_and_decodes(
    tmp_path: Path, offset: str | None, expected: int
) -> None:
    root = ET.Element("MasterDataSet")
    row = ET.SubElement(root, "t_key_index")
    record = {"key_id": "1", "period_type_id": "0", "length": "2", "position": "0", "period_offset": offset}
    for name, value in record.items():
        ET.SubElement(row, name).text = value
    archive = tmp_path / "optional-offset.zip"
    with ZipFile(archive, "w") as zipped:
        zipped.writestr("solution.xml", ET.tostring(root, encoding="utf-8"))
        zipped.writestr("t_data_0.BIN", struct.pack("<2d", 10.5, 20.5))
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite()
        assert solution.connection.execute("SELECT period_offset FROM t_key_index").fetchone() == (
            offset or None,
        )
        assert solution.connection.execute(
            "SELECT key_id, block_id, value FROM t_data_values ORDER BY block_id"
        ).fetchall() == [(1, expected + 1, 10.5), (1, expected + 2, 20.5)]
