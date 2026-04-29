# Creating a Database

PlexosDB supports creating a database from XML or from an empty in-memory
database initialized with `create_schema`.

## Create from XML

```python
from plexosdb import PlexosDB

# Loads records from XML and builds the database
db = PlexosDB.from_xml("/path/to/model.xml")
```

## Create empty schema (default)

```python
from plexosdb import PlexosDB

db = PlexosDB()
db.create_schema()
```

## Create empty schema and seed defaults

Use `seed_defaults=True` when you want a fresh DB that can immediately add
objects without importing XML first.

```python
from plexosdb import PlexosDB
from plexosdb.enums import ClassEnum

db = PlexosDB()
db.create_schema(seed_defaults=True)
db.add_object(ClassEnum.Generator, "GEN1")
```

## Use a custom schema SQL string

You can pass SQL directly with the `schema` parameter when you want full control
over table definitions (for example, creating a minimal schema for testing,
trying schema experiments, or adding project-specific tables). When provided,
this SQL is executed instead of the built-in default schema, so include every
table your workflow depends on (such as t_class, t_object, and related lookup
tables if you plan to add objects).

```python
from plexosdb import PlexosDB

schema = """
CREATE TABLE IF NOT EXISTS t_object (
    object_id     INTEGER PRIMARY KEY,
    name          TEXT,
    class_id      INTEGER,
    category_id   INTEGER,
    GUID          TEXT,
    description   TEXT
);

CREATE TABLE IF NOT EXISTS t_config (
	element TEXT PRIMARY KEY,
	value   TEXT
);

CREATE TABLE IF NOT EXISTS t_class (
	class_id INTEGER PRIMARY KEY,
	name TEXT,
	description TEXT,
	is_enabled INTEGER
);

INSERT INTO t_config(element, value) VALUES ('Version', '10.0');
INSERT INTO t_config(element, value) VALUES ('Dynamic', '1');

INSERT INTO t_class(class_id, name, description, is_enabled) VALUES (1, 'System', 'System class', 1);
INSERT INTO t_class(class_id, name, description, is_enabled) VALUES (2, 'Generator', 'Generator class', 1);

INSERT INTO t_object(object_id, name, class_id, category_id, GUID, description)
VALUES (1, 'System', 1, 1, '00000000-0000-0000-0000-000000000001', 'Default system');
"""

db = PlexosDB()
db.create_schema(schema=schema)
```
