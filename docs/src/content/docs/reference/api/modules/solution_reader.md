---
title: "SQLite Solution Reader"
---

The SQLite solution reader imports a PLEXOS solution ZIP into SQLite and
materializes derived result tables for analysis. Import it explicitly to
distinguish it from the DuckDB-backed solution wrapper:

```python
from plexosdb.solution_reader import PlexosSolution
```

## Display Helpers

## Result Types

See [Inspecting a PLEXOS Solution](/plexosdb/how-to/inspect_solution/) for a
complete ZIP-to-SQLite workflow.

<!-- Generated API reference -->

## Public module members

### plexosdb.solution_reader.solution

#### PlexosSolution

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/solution_reader/solution.py#L19)

Fluent interface for importing and querying a PLEXOS solution.

Two entry points are available:

* `from_zip` — bind to a PLEXOS solution ZIP file and use
  `to_sqlite` to import it.  Both XML metadata and BIN payloads
  are parsed during import.
* `from_sqlite` — open an already-imported SQLite database
  directly, without needing the original ZIP file.

Typical use with a ZIP::

    with PlexosSolution.from_zip("mysolution.zip") as sol:
        result = sol.to_sqlite("output.sqlite")
        sol.materialize_table("Generator")

Re-opening an existing database (no ZIP needed)::

    sol = PlexosSolution.from_sqlite("output.sqlite")
    show_db_tables(sol)
    sol.materialize_table("Generator")
    sol.close()

##### Methods and properties

###### from_zip

```text
from_zip(cls, path: str | Path, *, model_name: str | None=None) -> PlexosSolution
```

Create a `PlexosSolution` bound to a PLEXOS solution ZIP.

**Parameters**

- `path`
  Path to the PLEXOS solution ZIP file.
- `model_name`
  Optional hint for selecting the correct XML when multiple XML
  files exist inside the archive.

###### from_sqlite

```text
from_sqlite(cls, path: str | Path) -> PlexosSolution
```

Open an existing PLEXOS solution SQLite database without a source ZIP.

Useful for reading and querying a database that was previously created
with `to_sqlite` or `plexos_to_sqlite`.  No ZIP file is
required — the XML metadata and BIN payloads are already stored in
SQLite.

**Parameters**

- `path`
  Path to an existing PLEXOS solution SQLite file.

**Raises**

- `FileNotFoundError`
  If *path* does not exist.

###### to_sqlite

```text
to_sqlite(self, database: str | Path | None=None, *, if_exists: Literal['fail', 'reuse', 'replace']='reuse', materialize: Literal['none', 'all'] | Sequence[str]='none', decode_bin_values: bool=True) -> SQLiteResult
```

Import the solution ZIP into a SQLite database.

**Parameters**

- `database`
  Filesystem path for the SQLite file.  ``None`` (default) or the
  special string ``':memory:'`` create an in-memory database
  (``if_exists`` is ignored in that case).
- `if_exists`
  Controls behaviour when *database* already exists on disk:

  ``'fail'``
      Raise `FileExistsError`.
  ``'reuse'``
      Open the existing file, decode BIN values if missing, and
      attach derived-table schemas.  No re-import is performed.
  ``'replace'``
      Delete the file and create a fresh database.
- `decode_bin_values`
  If ``True`` (default), decode the BIN payload files from the
  solution ZIP into ``t_data_values``.  Set to ``False`` to skip
  BIN decoding — useful when only the table catalog or XML metadata
  tables are needed, which avoids writing potentially millions of
  rows and is significantly faster for large solutions.
- `materialize`
  Which derived tables to materialize after import:

  ``'none'``
      Do not materialize any tables (default).
  ``'all'``
      Materialize all available derived tables.
  sequence of strings
      Materialize only the named tables.

**Returns**

- `SQLiteResult`
  Contains the database path (``None`` for in-memory) and the list
  of table names in the main schema after import.

###### info

```text
info(self) -> SolutionInfo
```

Return metadata about the solution archive.

**Raises**

- `RuntimeError`
  If no ZIP path has been configured (see `from_zip`).

###### list_tables

```text
list_tables(self, *, schema: Literal['raw', 'processed', 'data', 'report']='report') -> list[TableInfo]
```

List tables available under the given *schema*.

**Parameters**

- `schema`
  ``'raw'``
      All tables present in the main SQLite schema.
  ``'processed'``
      Core PLEXOS entity tables (class, object, membership, property).
  ``'data'``
      Derived analysis tables (whether materialized or not).
  ``'report'``
      Same as *data* — derived tables exposed under the report schema.

###### materialize_table

```text
materialize_table(self, name: str, *, schema: Literal['data', 'report']='report', if_exists: Literal['fail', 'reuse', 'replace']='reuse') -> MaterializeResult
```

Materialize one derived table into the attached *schema*.

**Parameters**

- `name`
  Name of the derived table to materialize (e.g. ``'Generator'``).
- `schema`
  Target schema: ``'data'`` or ``'report'``.
- `if_exists`
  ``'reuse'`` (default) — return without re-materializing if the
  table already exists.  ``'fail'`` — raise `FileExistsError`.
  ``'replace'`` — drop the existing table and re-materialize.

###### connection

```text
connection: sqlite3.Connection
```

The active SQLite connection.

**Raises**

- `RuntimeError`
  If `to_sqlite` has not been called yet.

###### close

```text
close(self) -> None
```

Close the active SQLite connection.

###### source

```text
source: Path | None
```

Path to the source ZIP file, or ``None`` for `from_sqlite` instances.

###### name

```text
name: str
```

Display name for the solution.

Returns the stem of the source ZIP when available, then the stem of
the SQLite database, then ``'unknown'``.

### plexosdb.solution_reader.display

#### show_db_tables

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/solution_reader/display.py#L90)

Print the table catalog of a PLEXOS solution in DuckDB-style box format.

Collects all physical tables from attached SQLite schemas together with
logical derived result tables (``data`` / ``report``) from the solution
metadata, sorts them by schema then name, and prints the result as a
Unicode box table — the same visual style used by DuckDB.

This function must be called after `PlexosSolution.to_sqlite` has
been invoked (i.e. after the SQLite connection has been opened).

**Parameters**

- `client`
  A `PlexosSolution` instance with an active connection.
- `max_rows`
  Maximum number of rows to show before truncating with ``·`` rows.
  When the result exceeds *max_rows*, the first and last
  ``max_rows // 2`` rows are displayed.  Defaults to ``20``.

**Examples**

```python
from plexosdb import PlexosSolution, show_db_tables

sol = PlexosSolution.from_zip("my_solution.zip")
sol.to_sqlite("output.sqlite", if_exists="replace", decode_bin_values=False)

show_db_tables(sol)
```

```text
show_db_tables(client: PlexosSolution, *, max_rows: int=20) -> None
```

### plexosdb.solution_reader.types

#### SolutionInfo

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/solution_reader/types.py#L10)

Metadata about a PLEXOS solution archive.

#### SQLiteResult

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/solution_reader/types.py#L19)

Result returned by `PlexosSolution.to_sqlite`.

##### Methods and properties

###### is_in_memory

```text
is_in_memory: bool
```

Return *True* when the database lives in memory only.

#### TableInfo

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/solution_reader/types.py#L35)

Metadata about one table or view in a solution schema.

#### MaterializeResult

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/solution_reader/types.py#L45)

Result returned by `PlexosSolution.materialize_table`.

<!-- End generated API reference -->
