import pytest

from plexosdb.db import PlexosDB
from plexosdb.enums import ClassEnum
from plexosdb.exceptions import NotFoundError


def test_smoke_test():
    from plexosdb.db import PlexosDB  # noqa: F401


def test_initialize_instance():
    """Test creating a SQLiteManager instance."""
    db = PlexosDB()
    assert db is not None
    assert getattr(db, "_db") is not None
    assert isinstance(db, PlexosDB)


def test_create_schema_without_seed_defaults_keeps_lookup_tables_empty():
    """Default create_schema should not inject model metadata rows."""
    db = PlexosDB()
    db.create_schema()

    assert db.query("SELECT COUNT(*) FROM t_class")[0][0] == 0
    with pytest.raises(NotFoundError):
        db.add_object(ClassEnum.Generator, name="GEN1")


def test_create_schema_with_seed_defaults_supports_add_object():
    """Opt-in seed should bootstrap enough metadata for add_object workflows."""
    db = PlexosDB()
    db.create_schema(seed_defaults=True)

    assert db.query("SELECT COUNT(*) FROM t_class")[0][0] > 0
    object_id = db.add_object(ClassEnum.Generator, name="GEN1")
    assert object_id > 0


def test_create_schema_sets_default_version_in_config_when_row_exists():
    """create_schema should update existing Version row to default 9.2."""
    schema = """
    CREATE TABLE IF NOT EXISTS t_config (
        element TEXT PRIMARY KEY,
        value   TEXT
    );
    INSERT INTO t_config(element, value) VALUES ('Version', '0.0');
    """
    db = PlexosDB()
    db.create_schema(schema=schema)

    result = db.query("SELECT value FROM t_config WHERE element = ?", ("Version",))
    assert result
    assert result[0][0] == "9.2"


def test_create_schema_accepts_custom_version_in_config():
    """create_schema should apply custom version when Version row exists."""
    schema = """
    CREATE TABLE IF NOT EXISTS t_config (
        element TEXT PRIMARY KEY,
        value   TEXT
    );
    INSERT INTO t_config(element, value) VALUES ('Version', '0.0');
    """
    db = PlexosDB()
    db.create_schema(schema=schema, version="11.0")

    result = db.query("SELECT value FROM t_config WHERE element = ?", ("Version",))
    assert result
    assert result[0][0] == "11.0"


@pytest.mark.empty_database
@pytest.mark.parametrize(
    "table_name",
    [
        "t_assembly",
        "t_class_group",
        "t_config",
        "t_property_group",
        "t_unit",
        "t_action",
        "t_message",
        "t_property_tag",
        "t_custom_rule",
        "t_class",
        "t_collection",
        "t_collection_report",
        "t_property",
        "t_property_report",
        "t_custom_column",
        "t_attribute",
        "t_category",
        "t_object",
        "t_memo_object",
        "t_report",
        "t_object_meta",
        "t_attribute_data",
        "t_membership",
        "t_memo_membership",
        "t_membership_meta",
        "t_data",
        "t_date_from",
        "t_date_to",
        "t_tag",
        "t_text",
        "t_memo_data",
        "t_data_meta",
        "t_band",
    ],
)
def test_schema_creation(db_base, table_name):
    tables = db_base.query("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = [row[0] for row in tables]
    assert table_name in table_names
    table_name in db_base._db.tables


def test_get_plexos_version(db_base, _master_xml_param):
    """Verify that db.version matches the XML file version."""
    import re
    from pathlib import Path

    db = db_base

    xml_path = Path(_master_xml_param)
    stem = xml_path.stem

    match = re.search(r"(?:v|master_)([\d.]+)R", stem)
    assert match is not None
    version_str = match.group(1)
    expected_version = tuple(map(int, version_str.split(".")))

    assert db.version == expected_version
    assert db.get_plexos_version() == expected_version


def test_dynamic_config_enabled_after_xml_import(db_base):
    """Verify Dynamic config is enabled after XML import workflow."""
    result = db_base.query("SELECT value FROM t_config WHERE element = ?", ("Dynamic",))
    assert result
    assert result[0][0] == "1"


@pytest.mark.export
def test_export_to_xml(db_base, tmp_path):
    db = db_base
    fpath = tmp_path / "test.xml"
    db.to_xml(fpath)
    assert fpath.exists()


@pytest.mark.export
def test_xml_round_trip(db_base, tmp_path):
    original_db = db_base
    fpath = tmp_path / "test.xml"
    original_db.to_xml(fpath)
    assert fpath.exists()

    deserialized_db = PlexosDB.from_xml(fpath)
    tables = [
        table[0] for table in original_db._db.iter_query("SELECT name from sqlite_master WHERE type='table'")
    ]
    for table_name in tables:
        assert len(original_db.query(f"SELECT * FROM {table_name}")) == len(
            deserialized_db.query(f"SELECT * FROM {table_name}")
        ), "Different number of rows encounter."


@pytest.mark.export
def test_xml_not_exist():
    with pytest.raises(FileNotFoundError):
        _ = PlexosDB.from_xml("not/existing/path")


def test_from_xml_accepts_oversized_t_data_uid(tmp_path):
    xml_content = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<MasterDataSet>
    <t_data>
        <data_id>1</data_id>
        <uid>11339885002100928821</uid>
    </t_data>
</MasterDataSet>
"""
    xml_path = tmp_path / "oversized_uid.xml"
    xml_path.write_text(xml_content, encoding="utf-8")

    db = PlexosDB.from_xml(xml_path)
    rows = db.query("SELECT uid FROM t_data WHERE data_id = 1")
    assert len(rows) == 1
    assert rows[0][0] is not None


def test_plexosdb_version_property_refresh(db_with_topology):
    """Test PlexosDB.version property with cache refresh."""
    # First access should fetch version
    version1 = db_with_topology.version

    # Second access should use cached value
    version2 = db_with_topology.version

    # Should return same value
    assert version1 == version2


@pytest.mark.parametrize("version", [9, 10, 11, 12, "v10.0R2", (11, 0, 4)])
def test_create_schema_with_versioned_template(version):
    db = PlexosDB()
    db.create_schema(version=version)

    # Template import should populate metadata tables and set model version.
    class_count = db.query("SELECT COUNT(*) FROM t_class")[0][0]
    assert class_count > 0
    assert db.version is not None
    assert db.version[0] in {9, 10, 11, 12}


def test_create_schema_with_invalid_template_version_raises():
    db = PlexosDB()
    with pytest.raises(ValueError, match="Unsupported schema version"):
        db.create_schema(version=8)


def test_create_schema_twice_with_version_does_not_recreate_tables():
    db = PlexosDB()
    assert db.create_schema()
    assert db.create_schema(version=10)
    assert db.version is not None
    assert db.version[0] == 10
