# Creating a Database

PlexosDB supports creating a database from XML or from an empty in-memory
database initialized with `create_schema`.

## Create from XML

```python
from plexosdb import PlexosDB

# Loads records from XML and builds the database
db = PlexosDB.from_xml("/path/to/model.xml")
```

When using `from_xml(...)`, the schema is created automatically from the XML
content and metadata in that file.

## Create a New Empty Database with a Versioned Master Template

When starting from an empty database (instead of an existing XML), you can now
preload the versioned master template during schema creation.

```python
from plexosdb import PlexosDB

db_base = PlexosDB()

# Load default SQL schema + master template for PLEXOS v10
ok = db_base.create_schema(version=10)
assert ok
```

`create_schema(...)` returns a boolean status. It does not return a new
`PlexosDB` instance.

You can also pass custom SQL with `schema=...`:

```python
custom_schema = """
CREATE TABLE IF NOT EXISTS my_table (
	id INTEGER PRIMARY KEY,
	name TEXT
);
"""

db_custom = PlexosDB()
db_custom.create_schema(schema=custom_schema)
```

Supported template versions are:

- 9
- 10
- 11
- 12

Accepted version input formats include:

- `10`
- `"10.0"`
- `"v10.0R2"`
- `(10, 0, 2)`

```python
# Equivalent examples
db_base.create_schema(version="v11.0R4")
db_base.create_schema(version=(12, 0, 3))
```

If `version` is omitted, only the SQL schema is created (no master template is
imported).

Call `create_schema(...)` once per database instance. If the schema already
exists, re-running schema SQL is skipped.

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
