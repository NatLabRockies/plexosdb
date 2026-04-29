# Creating a Database

PlexosDB supports creating a database from XML or from an empty in-memory
database initialized with `create_schema`.

## Create from XML

```python
from plexosdb import PlexosDB

# Loads records from XML and builds the database
db = PlexosDB.from_xml("/path/to/model.xml")
```

## Create empty schema (tables only)

`create_schema()` by itself creates the table structure and config rows, but it
does not seed lookup/model rows such as `t_class`, collections, categories, and
the `System` object. This means high-level API workflows like `add_object(...)`
will not work until you either:

- use `seed_defaults=True`, or
- load/import data that provides those rows (for example `from_xml(...)`), or
- provide a custom `schema` SQL string that inserts the required seed data.

```python
from plexosdb import PlexosDB

db = PlexosDB()
db.create_schema()

# Default version in t_config is 9.2
assert db.query("SELECT value FROM t_config WHERE element='Version'")[0][0] == "9.2"
```

## Set schema version explicitly

Use `version="..."` when creating a fresh schema-only database and you want a
specific `t_config.Version` value.

```python
from plexosdb import PlexosDB

db = PlexosDB()
db.create_schema(version="11.0")
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

# If your custom schema does not provide Version, you can still set it here:
# db.create_schema(schema=schema, version="10.0")
```
