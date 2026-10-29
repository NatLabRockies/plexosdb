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


See [Inspecting a PLEXOS Solution](/plexosdb/how-to/inspect_solution/) for a complete
ZIP-to-SQLite workflow.

<!-- Generated API reference -->

## Public module members

### plexosdb.solution_reader.solution

#### PlexosSolution

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/solution_reader/solution.py#L19)

Fluent interface for importing and querying a PLEXOS solution.

##### Methods

###### from_zip

```text
from_zip(cls, path: str | Path, *, model_name: str | None=None) -> PlexosSolution
```

Create a :class:`PlexosSolution` bound to a PLEXOS solution ZIP.

###### from_sqlite

```text
from_sqlite(cls, path: str | Path) -> PlexosSolution
```

Open an existing PLEXOS solution SQLite database without a source ZIP.

###### to_sqlite

```text
to_sqlite(self, database: str | Path | None=None, *, if_exists: Literal['fail', 'reuse', 'replace']='reuse', materialize: Literal['none', 'all'] | Sequence[str]='none', decode_bin_values: bool=True) -> SQLiteResult
```

Import the solution ZIP into a SQLite database.

###### info

```text
info(self) -> SolutionInfo
```

Return metadata about the solution archive.

###### list_tables

```text
list_tables(self, *, schema: Literal['raw', 'processed', 'data', 'report']='report') -> list[TableInfo]
```

List tables available under the given *schema*.

###### materialize_table

```text
materialize_table(self, name: str, *, schema: Literal['data', 'report']='report', if_exists: Literal['fail', 'reuse', 'replace']='reuse') -> MaterializeResult
```

Materialize one derived table into the attached *schema*.

###### connection

```text
connection(self) -> sqlite3.Connection
```

The active SQLite connection.

###### close

```text
close(self) -> None
```

Close the active SQLite connection.

###### source

```text
source(self) -> Path | None
```

Path to the source ZIP file, or ``None`` for :meth:`from_sqlite` instances.

###### name

```text
name(self) -> str
```

Display name for the solution.

Full reference: [`PlexosSolution`](/plexosdb/reference/python-api/plexossolution/).

### plexosdb.solution_reader.display

#### show_db_tables

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/solution_reader/display.py#L90)

Print the table catalog of a PLEXOS solution in DuckDB-style box format.

```text
show_db_tables(client: PlexosSolution, *, max_rows: int=20) -> None
```

### plexosdb.solution_reader.types

#### SolutionInfo

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/solution_reader/types.py#L10)

Metadata about a PLEXOS solution archive.

#### SQLiteResult

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/solution_reader/types.py#L19)

Result returned by :meth:`PlexosSolution.to_sqlite`.

##### Methods

###### is_in_memory

```text
is_in_memory(self) -> bool
```

Return *True* when the database lives in memory only.

#### TableInfo

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/solution_reader/types.py#L35)

Metadata about one table or view in a solution schema.

Full reference: [`TableInfo`](/plexosdb/reference/python-api/tableinfo/).

#### MaterializeResult

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/solution_reader/types.py#L45)

Result returned by :meth:`PlexosSolution.materialize_table`.

<!-- End generated API reference -->
