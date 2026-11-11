---
title: "DuckDB Solution Reader"
---

The DuckDB solution reader converts a PLEXOS solution ZIP with `plexos2duckdb`
and exposes lazy DuckDB relations for analysis. Import it explicitly to
distinguish it from the SQLite-backed solution reader:

```python
from plexosdb.db_solution import PlexosSolution
```

## Result Types

See [Reading a PLEXOS Solution](/plexosdb/how-to/read_solution/) for a complete
ZIP-to-DuckDB workflow.

<!-- Generated API reference -->

## Public module members

### plexosdb.db_solution

#### PlexosSolution

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution.py#L40)

PLEXOS solution wrapper backed by ``plexos2duckdb``.

Passing ``database`` to `to_duckdb` creates or reuses a file-backed
DuckDB database, which is the fastest path for large solutions.  Omitting
``database`` keeps the result in memory by converting through a temporary
DuckDB file and copying it into an in-memory DuckDB connection.

##### Methods and properties

###### from_zip

```text
from_zip(cls, path: str | Path, *, model_name: str | None=None) -> PlexosSolution
```

Create a solution wrapper bound to a PLEXOS solution path.

###### to_duckdb

```text
to_duckdb(self, database: str | Path | None=None, *, if_exists: IfExists='reuse', n_threads: int | None=None, table_name_pattern: str | None=None, in_memory: bool | None=None) -> DuckDBResult
```

Convert the solution with ``plexos2duckdb`` and open a DuckDB connection.

**Parameters**

- `database`
  Output DuckDB path. When omitted, the result is in memory unless
  ``in_memory=False`` is provided.
- `if_exists`
  File-backed overwrite policy: ``'fail'``, ``'reuse'``, or ``'replace'``.
  Ignored for in-memory conversion because the intermediate database is
  temporary.
- `n_threads`
  Optional thread count passed to ``plexos2duckdb`` for time-series table writes.
- `table_name_pattern`
  Optional regex passed to ``plexos2duckdb`` to restrict generated data tables.
- `in_memory`
  ``True`` forces an in-memory final connection, ``False`` forces a
  file-backed database, and ``None`` uses in memory when *database* is omitted.

###### info

```text
info(self) -> DuckDBSolutionInfo
```

Return metadata about the configured or converted DuckDB solution.

###### list_tables

```text
list_tables(self, *, schema: DuckDBSchema='report') -> list[TableInfo]
```

List tables or views in one DuckDB solution schema.

###### sql

```text
sql(self, query_string: str) -> duckdb.DuckDBPyRelation
```

Build a lazy DuckDB relation from a SQL query.

###### query

```text
query(self, query_string: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[Any]
```

Execute a read-only query and return all rows.

###### query_dicts

```text
query_dicts(self, query_string: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[dict[str, Any]]
```

Execute a read-only query and return rows as dictionaries.

###### table

```text
table(self, table: str | ResultTable, *, schema: DuckDBSchema='report') -> duckdb.DuckDBPyRelation
```

Build a lazy DuckDB relation for a solution table or view.

###### list_objects_by_class

```text
list_objects_by_class(self, class_enum: ClassEnum | str, /, *, category: str | None=None) -> list[str]
```

Return solution object names for a PLEXOS class.

###### list_result_tables

```text
list_result_tables(self, *, schema: ResultSchema='report', phase: PhaseEnum | str | None=None, period: PeriodEnum | str | None=None, class_enum: ClassEnum | str | None=None, collection: CollectionEnum | str | None=None, property_name: str | None=None) -> list[ResultTable]
```

List result tables using PLEXOS class, collection, and property filters.

###### result_table

```text
result_table(self, *, schema: ResultSchema='report', phase: PhaseEnum | str=PhaseEnum.ST, period: PeriodEnum | str=PeriodEnum.INTERVAL, class_enum: ClassEnum | str | None=None, collection: CollectionEnum | str | None=None, property_name: str) -> ResultTable
```

Return one result table matching PLEXOS dimensions.

###### get_result

```text
get_result(self, table_name: ResultTable | str, /, *, object_names: str | Iterable[str] | None=None, category: str | None=None, sample_names: str | Iterable[str] | None='Mean', bands: int | Iterable[int] | None=None, start: str | None=None, end: str | None=None, columns: Sequence[str] | None=None) -> duckdb.DuckDBPyRelation
```

Build a lazy relation for filtered rows from a result table.

###### connection

```text
connection: duckdb.DuckDBPyConnection
```

The active DuckDB connection.

###### close

```text
close(self) -> None
```

Close the active DuckDB connection.

Full reference: [`PlexosSolution`](/plexosdb/reference/python-api/plexossolution/).

### plexosdb.db_solution_models

#### DuckDBSchema

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution_models.py#L11)

```text
DuckDBSchema = Literal['raw', 'processed', 'data', 'report']
```

#### IfExists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution_models.py#L12)

```text
IfExists = Literal['fail', 'reuse', 'replace']
```

#### ResultSchema

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution_models.py#L13)

```text
ResultSchema = Literal['data', 'report']
```

#### DuckDBResult

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution_models.py#L17)

Result returned by `plexosdb.db_solution.PlexosSolution.to_duckdb`.

##### Methods and properties

###### is_in_memory

```text
is_in_memory: bool
```

Return *True* when the database lives in memory only.

Full reference: [`DuckDBResult`](/plexosdb/reference/python-api/duckdbresult/).

#### DuckDBSolutionInfo

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution_models.py#L41)

Metadata about a DuckDB-backed PLEXOS solution.

Full reference: [`DuckDBSolutionInfo`](/plexosdb/reference/python-api/duckdbsolutioninfo/).

#### TableInfo

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution_models.py#L64)

Metadata about one table or view in a DuckDB solution schema.

Full reference: [`TableInfo`](/plexosdb/reference/python-api/tableinfo/).

#### ResultTable

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution_models.py#L79)

Metadata for one PLEXOS solution result table or view.

Full reference: [`ResultTable`](/plexosdb/reference/python-api/resulttable/).

<!-- End generated API reference -->
