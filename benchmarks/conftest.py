"""Shared fixtures for benchmark tests."""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest

from plexosdb import PlexosDB


@pytest.fixture(scope="function")
def db_instance_with_schema() -> Generator[PlexosDB, None, None]:
    """Create a minimal schema-backed database for benchmark runs."""
    db = PlexosDB()
    db.create_schema()
    with db._db.transaction():
        db._db.execute(
            "INSERT INTO t_class(class_id, name, description) VALUES (1, 'System', 'System class')"
        )
        db._db.execute(
            "INSERT INTO t_class(class_id, name, description) VALUES (2, 'Generator', 'Generator class')"
        )
        db._db.execute("INSERT INTO t_class(class_id, name, description) VALUES (3, 'Node', 'Node class')")
        db._db.execute(
            "INSERT INTO t_class(class_id, name, description) VALUES (4, 'Scenario', 'Scenario class')"
        )
        db._db.execute(
            "INSERT INTO t_class(class_id, name, description) VALUES (5, 'DataFile', 'DataFile class')"
        )
        db._db.execute(
            "INSERT INTO t_class(class_id, name, description) VALUES (6, 'Storage', 'Storage class')"
        )
        db._db.execute(
            "INSERT INTO t_class(class_id, name, description) VALUES (7, 'Report', 'Report class')"
        )
        db._db.execute("INSERT INTO t_class(class_id, name, description) VALUES (8, 'Model', 'Model class')")
        db._db.execute(
            "INSERT INTO t_object(object_id, name, class_id, GUID) VALUES (1, 'System', 1, ?)",
            (str(uuid.uuid4()),),
        )
        db._db.execute(
            "INSERT INTO t_collection(collection_id, parent_class_id, child_class_id, name) "
            "VALUES (1, 1, 2, 'Generators')"
        )
        db._db.execute(
            "INSERT INTO t_collection(collection_id, parent_class_id, child_class_id, name) "
            "VALUES (2, 1, 3, 'Nodes')"
        )
        db._db.execute(
            "INSERT INTO t_collection(collection_id, parent_class_id, child_class_id, name) "
            "VALUES (3, 2, 3, 'Nodes')"
        )
        db._db.execute(
            "INSERT INTO t_collection(collection_id, parent_class_id, child_class_id, name) "
            "VALUES (4, 1, 4, 'Scenarios')"
        )
        db._db.execute(
            "INSERT INTO t_collection(collection_id, parent_class_id, child_class_id, name) "
            "VALUES (5, 1, 6, 'Storages')"
        )
        db._db.execute(
            "INSERT INTO t_collection(collection_id, parent_class_id, child_class_id, name) "
            "VALUES (6, 1, 8, 'Models')"
        )
        db._db.execute(
            "INSERT INTO t_collection(collection_id, parent_class_id, child_class_id, name) "
            "VALUES (7, 8, 7, 'Models')"
        )
        db._db.execute(
            "INSERT INTO t_collection(collection_id, parent_class_id, child_class_id, name) "
            "VALUES (8, 1, 7, 'Reports')"
        )
        db._db.execute("INSERT INTO t_unit(unit_id, value) VALUES (1,'MW')")
        db._db.execute("INSERT INTO t_unit(unit_id, value) VALUES (2,'MWh')")
        db._db.execute("INSERT INTO t_unit(unit_id, value) VALUES (3,'%')")
        db._db.execute(
            "INSERT INTO t_collection(collection_id, parent_class_id, child_class_id, name) "
            "VALUES (?, ?, ?, ?)",
            (9, 8, 4, "Scenarios"),
        )
        db._db.execute(
            "INSERT INTO t_property(property_id, collection_id, unit_id, name) VALUES (1,1,1, 'Max Capacity')"
        )
        db._db.execute(
            "INSERT INTO t_property(property_id, collection_id, unit_id, name) VALUES (2,1,2, 'Max Energy')"
        )
        db._db.execute(
            "INSERT INTO t_property(property_id, collection_id, unit_id, name) "
            "VALUES (3,1,1, 'Rating Factor')"
        )
        db._db.execute("INSERT INTO t_config(element, value) VALUES ('Version', '10.0')")
        db._db.execute("INSERT INTO t_attribute(attribute_id, class_id, name) VALUES( 1, 2, 'Latitude')")
        db._db.execute(
            "INSERT INTO t_property_report(property_id, collection_id, name) VALUES (1, 1, 'Units')"
        )
    yield db
    db._db.close()
