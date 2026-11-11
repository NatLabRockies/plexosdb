---
title: "DuckDBResult"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution_models.py#L17)

Result returned by `plexosdb.db_solution.PlexosSolution.to_duckdb`.

## Import

```python
from plexosdb import DuckDBResult
```

## Declared fields

### database

```text
database: Annotated[Path | None, 'Filesystem path of the DuckDB file, or None for an in-memory database.'] = field(metadata={'description': 'Filesystem path of the DuckDB file, or None for an in-memory database.'})
```

### tables

```text
tables: Annotated[list[str], 'Names of tables present in the raw DuckDB schema after conversion.'] = field(default_factory=list, metadata={'description': 'Names of tables present in the raw DuckDB schema after conversion.'})
```

## Declared methods and properties

### is_in_memory

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db_solution_models.py#L35)

```text
is_in_memory: bool
```

Return *True* when the database lives in memory only.
