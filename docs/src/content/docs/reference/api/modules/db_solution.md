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

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/db_solution.py#L40)

PLEXOS solution wrapper backed by `plexos2duckdb`.

##### Methods

###### from_zip

```text
from_zip(cls, path: str | Path, *, model_name: str | None=None) -> PlexosSolution
```

Create a solution wrapper bound to a PLEXOS solution path.

###### to_duckdb

```text
to_duckdb(self, database: str | Path | None=None, *, if_exists: IfExists='reuse', n_threads: int | None=None, table_name_pattern: str | None=None, in_memory: bool | None=None) -> DuckDBResult
```

Convert the solution with `plexos2duckdb` and open a DuckDB connection.

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
connection(self) -> duckdb.DuckDBPyConnection
```

The active DuckDB connection.

###### close

```text
close(self) -> None
```

Close the active DuckDB connection.

Full reference:
[`PlexosSolution`](/plexosdb/reference/python-api/plexossolution/).

### plexosdb.db_solution_models

#### DuckDBSchema

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/db_solution_models.py#L11)

```text
DuckDBSchema = Literal['raw', 'processed', 'data', 'report']
```

#### IfExists

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/db_solution_models.py#L12)

```text
IfExists = Literal['fail', 'reuse', 'replace']
```

#### ResultSchema

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/db_solution_models.py#L13)

```text
ResultSchema = Literal['data', 'report']
```

#### DuckDBResult

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/db_solution_models.py#L17)

Result returned by :meth:`plexosdb.db_solution.PlexosSolution.to_duckdb`.

##### Methods

###### is_in_memory

```text
is_in_memory(self) -> bool
```

Return _True_ when the database lives in memory only.

Full reference: [`DuckDBResult`](/plexosdb/reference/python-api/duckdbresult/).

#### DuckDBSolutionInfo

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/db_solution_models.py#L41)

Metadata about a DuckDB-backed PLEXOS solution.

Full reference:
[`DuckDBSolutionInfo`](/plexosdb/reference/python-api/duckdbsolutioninfo/).

#### TableInfo

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/db_solution_models.py#L64)

Metadata about one table or view in a DuckDB solution schema.

Full reference: [`TableInfo`](/plexosdb/reference/python-api/tableinfo/).

#### ResultTable

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/db_solution_models.py#L79)

Metadata for one PLEXOS solution result table or view.

Full reference: [`ResultTable`](/plexosdb/reference/python-api/resulttable/).

<!-- End generated API reference -->
