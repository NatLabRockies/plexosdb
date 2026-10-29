---
title: "PlexosSolution"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L40)

PLEXOS solution wrapper backed by ``plexos2duckdb``.

## Import

```python
from plexosdb import PlexosSolution
```

## Declared fields

### _zip_path

```text
_zip_path: Path | None
```

### _model_name

```text
_model_name: str | None
```

### _database_path

```text
_database_path: Path | None
```

### _connection

```text
_connection: duckdb.DuckDBPyConnection | None
```

## Constructor

```text
__init__(self, source_path: str | Path | None=None, *, model_name: str | None=None, _factory_token: object | None=None) -> None
```

## Declared methods

### from_zip

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L75)

```text
from_zip(cls, path: str | Path, *, model_name: str | None=None) -> PlexosSolution
```

Create a solution wrapper bound to a PLEXOS solution path.

### to_duckdb

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L84)

```text
to_duckdb(self, database: str | Path | None=None, *, if_exists: IfExists='reuse', n_threads: int | None=None, table_name_pattern: str | None=None, in_memory: bool | None=None) -> DuckDBResult
```

Convert the solution with ``plexos2duckdb`` and open a DuckDB connection.

### info

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L132)

```text
info(self) -> DuckDBSolutionInfo
```

Return metadata about the configured or converted DuckDB solution.

### list_tables

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L141)

```text
list_tables(self, *, schema: DuckDBSchema='report') -> list[TableInfo]
```

List tables or views in one DuckDB solution schema.

### sql

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L161)

```text
sql(self, query_string: str) -> duckdb.DuckDBPyRelation
```

Build a lazy DuckDB relation from a SQL query.

### query

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L165)

```text
query(self, query_string: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[Any]
```

Execute a read-only query and return all rows.

### query_dicts

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L173)

```text
query_dicts(self, query_string: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[dict[str, Any]]
```

Execute a read-only query and return rows as dictionaries.

### table

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L181)

```text
table(self, table: str | ResultTable, *, schema: DuckDBSchema='report') -> duckdb.DuckDBPyRelation
```

Build a lazy DuckDB relation for a solution table or view.

### list_objects_by_class

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L190)

```text
list_objects_by_class(self, class_enum: ClassEnum | str, /, *, category: str | None=None) -> list[str]
```

Return solution object names for a PLEXOS class.

### list_result_tables

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L200)

```text
list_result_tables(self, *, schema: ResultSchema='report', phase: PhaseEnum | str | None=None, period: PeriodEnum | str | None=None, class_enum: ClassEnum | str | None=None, collection: CollectionEnum | str | None=None, property_name: str | None=None) -> list[ResultTable]
```

List result tables using PLEXOS class, collection, and property filters.

### result_table

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L221)

```text
result_table(self, *, schema: ResultSchema='report', phase: PhaseEnum | str=PhaseEnum.ST, period: PeriodEnum | str=PeriodEnum.INTERVAL, class_enum: ClassEnum | str | None=None, collection: CollectionEnum | str | None=None, property_name: str) -> ResultTable
```

Return one result table matching PLEXOS dimensions.

### get_result

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L242)

```text
get_result(self, table_name: ResultTable | str, /, *, object_names: str | Iterable[str] | None=None, category: str | None=None, sample_names: str | Iterable[str] | None='Mean', bands: int | Iterable[int] | None=None, start: str | None=None, end: str | None=None, columns: Sequence[str] | None=None) -> duckdb.DuckDBPyRelation
```

Build a lazy relation for filtered rows from a result table.

### connection

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L269)

```text
connection(self) -> duckdb.DuckDBPyConnection
```

The active DuckDB connection.

### close

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution.py#L275)

```text
close(self) -> None
```

Close the active DuckDB connection.

