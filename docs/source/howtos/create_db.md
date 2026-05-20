# Creating a database from an existing XML file

PlexosDB allows you to create a database from an existing XML file using a few
simple steps.

## Basic Usage

```python
from plexosdb import PlexosDB

# Create a new database
db = PlexosDB.from_xml("/path/to/xml")
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
