---
title: "Importing and Exporting Data"
---

PlexosDB provides methods for importing data from XML files and exporting to XML
or CSV formats.

## Importing from XML

Create a database from an existing PLEXOS XML file:

```python
from plexosdb import PlexosDB

# Create database from XML
db = PlexosDB.from_xml("/path/to/model.xml")

# Check PLEXOS version of the imported model
version = db.version
print(f"Imported PLEXOS model version: {version}")
```

After importing, see
[Validating a Database](/plexosdb/how-to/validate_database/) to check model
consistency and write findings to a text report.

## Importing a PLEXOS solution ZIP and reading report tables

Use `PlexosSolution` when you want to analyze PLEXOS solution ZIP outputs. With
the default `materialize="none"`, you can materialize only the table you need.

```python
from plexosdb.solution_reader import PlexosSolution
import pandas as pd

PLEXOS_SOLUTION = "/path/to/solution.zip"

sol = PlexosSolution.from_zip(PLEXOS_SOLUTION)
sol.to_sqlite("output.sqlite", if_exists="replace")

table = "ST__Interval__Regions__Fixed_Load"
sol.materialize_table(table, schema="report")
df_table = pd.read_sql_query(f'SELECT * FROM report."{table}"', sol.connection)
```

How to use this flow:

1. Create a `PlexosSolution` via `PlexosSolution.from_zip(zip_path)`.
2. Call `to_sqlite(path, if_exists="replace")` to import the ZIP into SQLite.
   Use `materialize="none"` (default) to avoid materializing every derived table
   up-front.
3. Call `materialize_table(table, schema="report")` for the specific table you
   want.
4. Read that table with pandas using `pd.read_sql_query(...)` and
   `sol.connection`.

## Exporting to XML

Export your database to a PLEXOS-compatible XML file:

```python
from pathlib import Path

# Export the entire database to XML
output_path = Path("/path/to/output_model.xml")
success = db.to_xml(output_path)

if success:
    print(f"Model exported successfully to {output_path}")
else:
    print("Export failed")
```

## CSV and database backups

Export tables to a directory as `<table>.csv` files, then import those files
into an existing database with the matching schema:

```python
# Export every non-internal table, or select specific tables.
db.to_csv("/path/to/model-csv")
db.to_csv("/path/to/model-csv", tables=["t_object", "t_data"])

# The target database must already have the corresponding tables.
restored = PlexosDB()
restored.create_schema()
restored.import_from_csv("/path/to/model-csv")
```

`import_from_csv()` appends rows and imports the selected tables atomically. A
single `<table>.csv` file can also be imported directly. CSV exports include a
header row; `\N` represents NULL, backslash-prefixed strings are escaped, and
BLOB values are written as base64 with a `\B` prefix.

Back up an in-memory or file-backed SQLite database to a separate file:

```python
db.backup_database("/path/to/backups/model.sqlite")
```

The backup method creates missing parent directories and rejects a destination
that is the same file as the source database.

## Creating databases

```python
# Create an empty database
db = PlexosDB()
db.create_schema(version=10)

```

:::caution

When working with large XML or CSV files, ensure you have sufficient memory and
disk space for the operations.

:::
