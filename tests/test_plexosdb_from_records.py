from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from plexosdb import PlexosDB


def test_bulk_insert_properties_from_records(db_base: PlexosDB):
    from plexosdb import ClassEnum, CollectionEnum

    db: PlexosDB = db_base

    db.add_object(ClassEnum.Generator, "Generator1")
    db.add_object(ClassEnum.Generator, "Generator2")
    db.add_object(ClassEnum.Generator, "Generator3")

    records = [
        {
            "name": "Generator1",
            "properties": {
                "Max Capacity": {"value": 100.0},
                "Min Stable Level": {"value": 20.0},
                "Heat Rate": {"value": 10.5},
            },
        },
        {
            "name": "Generator2",
            "properties": {
                "Max Capacity": {"value": 150.0},
                "Min Stable Level": {"value": 30.0},
                "Heat Rate": {"value": 9.8},
            },
        },
        {
            "name": "Generator3",
            "properties": {
                "Max Capacity": {"value": 200.0},
                "Min Stable Level": {"value": 40.0},
                "Heat Rate": {"value": 8.7},
            },
        },
    ]

    db.add_properties_from_records(
        records,
        object_class=ClassEnum.Generator,
        collection=CollectionEnum.Generators,
        scenario="Base Case",
    )

    properties = db.get_object_properties(ClassEnum.Generator, name="Generator1")
    assert properties
    assert properties[0]["property"] == "Max Capacity"
    assert properties[0]["scenario_name"] == "Base Case"


def test_add_properties_supports_flat_records_with_metadata(db_instance_with_schema: PlexosDB):
    from datetime import datetime
    from plexosdb import ClassEnum, CollectionEnum

    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "FlatGen")

    records = [
        {
            "name": "FlatGen",
            "property": "Max Capacity",
            "value": 120.5,
            "band": 1,
            "date_from": datetime(2025, 1, 1),
            "date_to": datetime(2025, 2, 1),
        },
        {
            "name": "FlatGen",
            "property": "Max Energy",
            "value": 350.0,
            "datafile_text": "profile.csv",
        },
    ]

    db.add_properties_from_records(
        records,
        object_class=ClassEnum.Generator,
        collection=CollectionEnum.Generators,
        parent_class=ClassEnum.System,
        scenario="Planning",
    )

    data_rows = db._db.fetchall("SELECT membership_id, property_id, value FROM t_data")
    assert len(data_rows) == 2

    band_rows = db._db.fetchall("SELECT data_id, band_id FROM t_band")
    assert len(band_rows) == 1
    assert band_rows[0][1] == 1

    date_from_rows = db._db.fetchall("SELECT date FROM t_date_from")
    date_to_rows = db._db.fetchall("SELECT date FROM t_date_to")
    assert date_from_rows[0][0].startswith("2025-01-01")
    assert date_to_rows[0][0].startswith("2025-02-01")

    text_rows = db._db.fetchall("SELECT class_id, value FROM t_text")
    assert len(text_rows) == 1
    assert text_rows[0][1] == "profile.csv"


def test_add_properties_nested_records_emit_deprecation(db_instance_with_schema: PlexosDB):
    from plexosdb import ClassEnum, CollectionEnum

    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "LegacyGen")

    records = [
        {
            "name": "LegacyGen",
            "properties": {
                "Max Capacity": {"value": 75.0},
            },
        }
    ]

    with pytest.warns(DeprecationWarning):
        db.add_properties_from_records(
            records,
            object_class=ClassEnum.Generator,
            collection=CollectionEnum.Generators,
            parent_class=ClassEnum.System,
            scenario="Legacy",
        )

    values = db._db.fetchall("SELECT value FROM t_data")
    assert values == [(75.0,)]


def test_bulk_insert_memberships_from_records(db_base: PlexosDB):
    from plexosdb import ClassEnum, CollectionEnum

    db = db_base

    objects = list(f"Generator_{i}" for i in range(5))
    db.add_objects(ClassEnum.Generator, objects)
    parent_object_ids = db.get_objects_id(objects, class_enum=ClassEnum.Generator)
    assert parent_object_ids
    assert db.get_memberships_system(objects, object_class=ClassEnum.Generator)

    objects = list(f"Nodes_{i}" for i in range(5))
    db.add_objects(ClassEnum.Node, objects)
    child_object_ids = db.get_objects_id(objects, class_enum=ClassEnum.Node)
    assert child_object_ids
    assert len(child_object_ids) == 5
    assert db.get_memberships_system(objects, object_class=ClassEnum.Node)

    collection_id = db.get_collection_id(
        CollectionEnum.Nodes, parent_class_enum=ClassEnum.Generator, child_class_enum=ClassEnum.Node
    )
    parent_class_id = db.get_class_id(ClassEnum.Generator)
    child_class_id = db.get_class_id(ClassEnum.Node)
    memberships = [
        {
            "collection_id": collection_id,
            "parent_class_id": parent_class_id,
            "child_class_id": child_class_id,
            "child_object_id": child_id,
            "parent_object_id": parent_id,
        }
        for parent_id, child_id in zip(parent_object_ids, child_object_ids)
    ]
    db.add_memberships_from_records(memberships)

    db_memberships = db.list_object_memberships(
        ClassEnum.Node,
        objects[0],
        collection=CollectionEnum.Nodes,
    )
    assert len(db_memberships) == 2  # 1 + system membership

    memberships = [
        {
            "parent_class_id": parent_class_id,
            "child_class_id": child_class_id,
            "child_object_id": child_id,
            "parent_object_id": parent_id,
        }
        for parent_id, child_id in zip(parent_object_ids, child_object_ids)
    ]
    with pytest.raises(KeyError):
        _ = db.add_memberships_from_records(memberships)


def test_bulk_insert_memberships_from_records_respects_chunksize(
    db_instance_with_schema: PlexosDB,
    monkeypatch: pytest.MonkeyPatch,
):
    from plexosdb import ClassEnum, CollectionEnum

    db = db_instance_with_schema
    parent_names = [f"ChunkGen_{idx}" for idx in range(5)]
    child_names = [f"ChunkNode_{idx}" for idx in range(5)]

    db.add_objects(ClassEnum.Generator, *parent_names)
    db.add_objects(ClassEnum.Node, *child_names)

    parent_object_ids = db.get_objects_id(parent_names, class_enum=ClassEnum.Generator)
    child_object_ids = db.get_objects_id(child_names, class_enum=ClassEnum.Node)
    parent_class_id = db.get_class_id(ClassEnum.Generator)
    child_class_id = db.get_class_id(ClassEnum.Node)
    collection_id = db.get_collection_id(
        CollectionEnum.Nodes,
        parent_class_enum=ClassEnum.Generator,
        child_class_enum=ClassEnum.Node,
    )
    memberships = [
        {
            "collection_id": collection_id,
            "parent_class_id": parent_class_id,
            "child_class_id": child_class_id,
            "child_object_id": child_id,
            "parent_object_id": parent_id,
        }
        for parent_id, child_id in zip(parent_object_ids, child_object_ids)
    ]

    observed_batch_sizes: list[int] = []
    original_executemany = db._db.executemany

    def spy_executemany(query, params_seq):
        observed_batch_sizes.append(len(params_seq))
        return original_executemany(query, params_seq)

    monkeypatch.setattr(db._db, "executemany", spy_executemany)
    db.add_memberships_from_records(memberships, chunksize=2)

    assert observed_batch_sizes == [2, 2, 1]


def test_bulk_insert_memberships_from_records_rejects_non_positive_chunksize(
    db_instance_with_schema: PlexosDB,
):
    db = db_instance_with_schema
    membership = {
        "parent_class_id": 2,
        "parent_object_id": 1,
        "collection_id": 3,
        "child_class_id": 3,
        "child_object_id": 1,
    }

    with pytest.raises(ValueError, match="chunksize must be >= 1"):
        db.add_memberships_from_records([membership], chunksize=0)


def test_bulk_insert_memberships_from_records_accepts_empty_records(
    db_instance_with_schema: PlexosDB,
):
    db = db_instance_with_schema

    assert db.add_memberships_from_records([]) is True


def test_bulk_insert_memberships_from_records_invalid_keys_shape(
    db_instance_with_schema: PlexosDB,
):
    db = db_instance_with_schema
    invalid_membership = {
        "parent_class_id": 2,
        "parent_object_id": 1,
        "collection_id": 3,
        "child_class_id": 3,
        "bad_key": 1,
    }

    with pytest.raises(KeyError, match="Some of the records do not have all the required fields"):
        db.add_memberships_from_records([invalid_membership])


def test_add_properties_from_records_no_records(db_instance_with_schema: PlexosDB, caplog):
    """Gracefully handle empty payload."""
    from plexosdb import ClassEnum, CollectionEnum

    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "EmptyGen")

    db.add_properties_from_records(
        [],
        object_class=ClassEnum.Generator,
        collection=CollectionEnum.Generators,
        parent_class=ClassEnum.System,
        scenario="None",
    )

    assert "No records provided" in caplog.text
    assert db._db.fetchone("SELECT COUNT(*) FROM t_data")[0] == 0


def test_add_properties_from_records_unknown_property(db_instance_with_schema: PlexosDB):
    """Return early when properties are not recognized for the collection."""
    from plexosdb import ClassEnum, CollectionEnum

    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "BadPropGen")

    db.add_properties_from_records(
        [{"name": "BadPropGen", "property": "Unknown", "value": 1}],
        object_class=ClassEnum.Generator,
        collection=CollectionEnum.Generators,
        parent_class=ClassEnum.System,
        scenario="None",
    )

    assert db._db.fetchone("SELECT COUNT(*) FROM t_data")[0] == 0


def test_add_properties_from_records_respects_parent_membership(db_with_topology: PlexosDB):
    from plexosdb import ClassEnum, CollectionEnum
    from plexosdb.exceptions import NotFoundError

    db = db_with_topology
    system_name = db.list_objects_by_class(ClassEnum.System)[0]
    system_membership_id = db.get_membership_id(system_name, "node-01", CollectionEnum.Nodes)
    db._db.execute("DELETE FROM t_membership WHERE membership_id = ?", (system_membership_id,))

    with pytest.raises(NotFoundError, match="Objects not found"):
        db.add_properties_from_records(
            [{"name": "node-01", "property": "Load", "value": 123.0}],
            object_class=ClassEnum.Node,
            parent_class=ClassEnum.System,
            collection=CollectionEnum.Nodes,
            scenario="Base Case",
        )

    assert db._db.fetchone("SELECT COUNT(*) FROM t_data")[0] == 0


def test_add_properties_from_records_non_system_parent(db_with_topology: PlexosDB):
    from plexosdb import ClassEnum, CollectionEnum

    db = db_with_topology

    db.add_object(ClassEnum.Reserve, "TestReserve")
    db.add_membership(
        ClassEnum.Reserve,
        ClassEnum.Region,
        "TestReserve",
        "region-01",
        CollectionEnum.Regions,
    )

    records = [{"name": "region-01", "property": "Load Risk", "value": 5.0}]
    db.add_properties_from_records(
        records,
        object_class=ClassEnum.Region,
        parent_class=ClassEnum.Reserve,
        collection=CollectionEnum.Regions,
        scenario="Base",
    )

    data_count = db._db.fetchone("SELECT COUNT(*) FROM t_data")[0]
    assert data_count == 1


def test_get_memberships_system_chunks_over_900_names(db_base: PlexosDB):
    """get_memberships_system passes a tuple (not list) to fetchall_dict when >900 names.

    Regression test: the params were previously built as a list[Any], which is incompatible
    with SQLiteManager.fetchall_dict's expected tuple[Any, ...] parameter type.
    """
    from plexosdb import ClassEnum

    db = db_base
    names = [f"ChunkGen_{i}" for i in range(950)]
    db.add_objects(ClassEnum.Generator, names)

    result = db.get_memberships_system(names, object_class=ClassEnum.Generator)
    assert len(result) == 950
    assert {r["name"] for r in result} == set(names)


def _seed_model_attributes(db: PlexosDB) -> None:
    from plexosdb import ClassEnum

    class_id = db.get_class_id(ClassEnum.Model)

    db._db.executemany(
        """
        INSERT INTO t_attribute (attribute_id, class_id, name)
        VALUES (?, ?, ?)
        """,
        [
            (1001, class_id, "Enabled"),
            (1002, class_id, "Random Number Seed"),
        ],
    )


def test_add_attributes_from_records_explicit_format(db_instance_with_schema: PlexosDB):
    from plexosdb import ClassEnum

    db = db_instance_with_schema
    _seed_model_attributes(db)
    db.add_object(ClassEnum.Model, "AttrModel")

    records = [
        {"name": "AttrModel", "attribute": "Enabled", "value": -1},
        {"name": "AttrModel", "attribute": "Random Number Seed", "value": 1000},
    ]

    db.add_attributes_from_records(records, object_class=ClassEnum.Model)

    rows = db._db.fetchall(
        """
        SELECT attr.name, data.value, data.state
        FROM t_attribute_data AS data
        JOIN t_attribute AS attr ON attr.attribute_id = data.attribute_id
        JOIN t_object AS obj ON obj.object_id = data.object_id
        WHERE obj.name = ?
        ORDER BY attr.name
        """,
        ("AttrModel",),
    )

    assert rows == [
        ("Enabled", -1.0, None),
        ("Random Number Seed", 1000.0, None),
    ]


def test_add_attributes_from_records_wide_format(db_instance_with_schema: PlexosDB):
    from plexosdb import ClassEnum

    db = db_instance_with_schema
    _seed_model_attributes(db)
    db.add_object(ClassEnum.Model, "WideAttrModel")

    db.add_attributes_from_records(
        [{"name": "WideAttrModel", "Enabled": -1, "Random Number Seed": 1000}],
        object_class=ClassEnum.Model,
    )

    rows = db._db.fetchall(
        """
        SELECT attr.name, data.value
        FROM t_attribute_data AS data
        JOIN t_attribute AS attr ON attr.attribute_id = data.attribute_id
        JOIN t_object AS obj ON obj.object_id = data.object_id
        WHERE obj.name = ?
        ORDER BY attr.name
        """,
        ("WideAttrModel",),
    )

    assert rows == [
        ("Enabled", -1.0),
        ("Random Number Seed", 1000.0),
    ]


def test_add_attributes_from_records_rejects_duplicates(db_instance_with_schema: PlexosDB):
    from plexosdb import ClassEnum

    db = db_instance_with_schema
    _seed_model_attributes(db)
    db.add_object(ClassEnum.Model, "DuplicateAttrModel")

    records = [
        {"name": "DuplicateAttrModel", "Enabled": -1},
        {"name": "DuplicateAttrModel", "Enabled": 0},
    ]

    with pytest.raises(ValueError, match="Duplicate attribute record"):
        db.add_attributes_from_records(records, object_class=ClassEnum.Model)

    assert db._db.fetchone("SELECT COUNT(*) FROM t_attribute_data")[0] == 0


def test_add_attributes_from_records_unknown_attribute(db_instance_with_schema: PlexosDB):
    from plexosdb import ClassEnum

    db = db_instance_with_schema
    _seed_model_attributes(db)
    db.add_object(ClassEnum.Model, "BadAttrModel")

    with pytest.raises(KeyError, match="Invalid attribute record"):
        db.add_attributes_from_records(
            [{"name": "BadAttrModel", "Fake Attribute": 123}],
            object_class=ClassEnum.Model,
        )

    assert db._db.fetchone("SELECT COUNT(*) FROM t_attribute_data")[0] == 0


def test_add_attributes_from_records_respects_chunksize(
    db_instance_with_schema: PlexosDB,
    monkeypatch: pytest.MonkeyPatch,
):
    from plexosdb import ClassEnum

    db = db_instance_with_schema
    _seed_model_attributes(db)
    names = [f"ChunkAttrModel_{idx}" for idx in range(5)]
    db.add_objects(ClassEnum.Model, *names)

    records = [{"name": name, "Enabled": -1} for name in names]

    observed_batch_sizes: list[int] = []
    original_executemany = db._db.executemany

    def spy_executemany(query, params_seq):
        observed_batch_sizes.append(len(params_seq))
        return original_executemany(query, params_seq)

    monkeypatch.setattr(db._db, "executemany", spy_executemany)
    db.add_attributes_from_records(records, object_class=ClassEnum.Model, chunksize=2)

    assert observed_batch_sizes == [2, 2, 1]


def test_add_attributes_from_records_rejects_non_positive_chunksize(
    db_instance_with_schema: PlexosDB,
):
    from plexosdb import ClassEnum

    db = db_instance_with_schema
    _seed_model_attributes(db)
    db.add_object(ClassEnum.Model, "BadChunkAttrModel")

    with pytest.raises(ValueError, match="chunksize must be >= 1"):
        db.add_attributes_from_records(
            [{"name": "BadChunkAttrModel", "Enabled": -1}],
            object_class=ClassEnum.Model,
            chunksize=0,
        )
