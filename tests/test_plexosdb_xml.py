import os
import sqlite3
from contextlib import closing
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from plexosdb import ClassEnum, PlexosDB
from plexosdb.enums import Schema
from plexosdb.xml_handler import XMLHandler, xml_query

XML_FPATH = Path("tests").joinpath("data/run_of_river_case/TestSystem.xml")
NAMESPACE = "http://tempuri.org/MasterDataSet.xsd"


@pytest.mark.parametrize(
    "value, expected",
    [
        ("-1", "-1"),
        ("1001", "1001"),
        ("0", "0"),
        ("2147483647", "2147483647"),
        ("-2147483648", "-2147483648"),
        ("1001.0", "1001"),
        ("10.125", "10.125"),
        ("-0.5", "-0.5"),
        ("1e-20", "1e-20"),
        ("1.0000000000000002", "1.0000000000000002"),
        ("filename.csv", "filename.csv"),
    ],
)
def test_attribute_values_round_trip_as_plexos_xml(tmp_path: Path, value: str, expected: str) -> None:
    source = tmp_path / "source.xml"
    source.write_text(
        f'<MasterDataSet xmlns="{NAMESPACE}">'
        "<t_attribute_data><object_id>1</object_id><attribute_id>1</attribute_id>"
        f"<value>{value}</value></t_attribute_data></MasterDataSet>",
        encoding="utf-8",
    )
    db = PlexosDB.from_xml(source)
    target = tmp_path / "export.xml"
    db.to_xml(target)

    root = ET.parse(target).getroot()
    assert root is not None
    assert root.findtext(f"{{{NAMESPACE}}}t_attribute_data/{{{NAMESPACE}}}value") == expected
    imported = PlexosDB.from_xml(target)
    assert imported.query("SELECT value FROM t_attribute_data") == db.query(
        "SELECT value FROM t_attribute_data"
    )


@pytest.mark.parametrize(
    "table, value, expected",
    [
        ("t_attribute_data", -1, "-1"),
        ("t_attribute_data", None, None),
        ("t_attribute_data", float("inf"), "inf"),
        ("t_data", 1001.0, "1001.0"),
        ("t_attribute", 1001.0, "1001.0"),
    ],
)
def test_export_preserves_other_value_types(
    table: str, value: int | float | None, expected: str | None
) -> None:
    handler = XMLHandler(initialize=True)
    handler.create_table_element([(value,)], {"value": "FLOAT"}, table)

    element = handler.root.find(f"{table}/value")
    if expected is None:
        assert element is None
    else:
        assert element is not None
        assert element.text == expected


@pytest.fixture
def xml_tree(_master_xml_param):
    return ET.parse(_master_xml_param)


def test_get_root(xml_tree):
    root = xml_tree.getroot()
    assert root is not None


@pytest.fixture(scope="module")
def xml_handler(_master_xml_param):
    return XMLHandler(fpath=_master_xml_param, namespace=NAMESPACE)


def test_xmlhandler_instance(xml_handler, xml_tree, _master_xml_param):
    assert isinstance(xml_handler, XMLHandler)
    assert type(xml_handler.tree) is type(xml_tree)
    assert xml_handler.fpath == _master_xml_param
    assert xml_handler.namespace == NAMESPACE


@pytest.mark.parametrize("in_memory", [True, False])
def test_in_memory_initialization(in_memory, _master_xml_param):
    handler = XMLHandler.parse(fpath=_master_xml_param, in_memory=in_memory)
    assert isinstance(handler, XMLHandler)
    assert handler.in_memory == in_memory
    assert handler.fpath == _master_xml_param
    assert handler.namespace == NAMESPACE
    elements = list(handler.iter(Schema.Objects))
    assert len(elements) > 0


def test_cache_construction():
    handler = XMLHandler.parse(fpath=XML_FPATH, in_memory=True)
    assert handler._cache is not None
    assert len(handler._cache) > 0


def test_iter(xml_handler):
    elements = list(xml_handler.iter(Schema.Objects))
    assert len(elements) > 4


def test_get_records(xml_handler):
    elements = list(xml_handler.get_records(Schema.Objects))
    assert len(elements) > 0
    assert elements[0]["class_id"] == 1


def test_save_xml(tmp_path):
    handler = XMLHandler.parse(fpath=XML_FPATH, in_memory=True)
    handler.to_xml(tmp_path / ".xml")

    assert os.path.exists(tmp_path / ".xml")
    assert getattr(handler, "_cache", False) is False
    assert getattr(handler, "_counts", False) is False


@pytest.mark.parametrize(
    "element_name, tags, tag_elements, expected_query",
    [
        ("t_object", (), {"class_id": "2"}, './/t_object[class_id="2"]'),
        ("t_object", (), {"class_id": "2", "enum_id": "1"}, './/t_object[class_id="2"][enum_id="1"]'),
        (
            "t_object",
            ("name",),
            {"class_id": "2", "enum_id": "1"},
            './/t_object[name][class_id="2"][enum_id="1"]',
        ),
    ],
)
def test_xml_query(element_name, tags, tag_elements, expected_query):
    assert xml_query(element_name, *tags, **tag_elements) == expected_query


def test_iter_with_elements(xml_handler):
    """Test XMLHandler.iter() with specific elements filters."""
    from plexosdb.enums import Schema

    # Get elements with specific IDs to exercise the filter path
    elements = list(xml_handler.iter(Schema.Objects, 1))
    assert elements is not None
    assert isinstance(elements, list)


def test_cache_iter_with_label_filter(xml_handler):
    """Test XMLHandler._cache_iter() with label-based filtering."""
    from plexosdb.enums import Schema

    # This exercises the code path where label validation occurs
    element_type = Schema.Objects

    if element_type.label:
        # Create tag_elements dict with the label
        elements = list(xml_handler._cache_iter(element_type, **{element_type.label: 1}))
        assert isinstance(elements, list)


@pytest.mark.parametrize("in_memory", [True, False])
def test_complex_like_object_names(in_memory: bool) -> None:
    handler = XMLHandler.parse(fpath="tests/data/complex_object_names.xml", in_memory=in_memory)
    records = handler.get_records(Schema.Objects)
    assert [(record["name"], record["object_id"]) for record in records] == [("7706j", 1), ("7999j", 2)]


def test_complex_like_object_names_round_trip(tmp_path: Path) -> None:
    source = Path("tests/data/complex_object_names.xml")
    expected = {"7706j": 1, "7999j": 2}
    exported = tmp_path / "complex_object_names.xml"
    for path in (source, exported):
        with closing(sqlite3.connect(":memory:")) as connection:
            db = PlexosDB.from_xml(path, fpath_or_conn=connection)
            assert set(db.list_objects_by_class(ClassEnum.Generator)) == set(expected)
            for name, object_id in expected.items():
                assert db.get_object_id(ClassEnum.Generator, name) == object_id
            if path == source:
                assert db.to_xml(exported)
                names = [element.text for element in ET.parse(exported).findall(".//{*}t_object/{*}name")]
                assert set(names) == set(expected)
