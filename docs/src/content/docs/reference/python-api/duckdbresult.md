---
title: "DuckDBResult"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution_models.py#L17)

Result returned by :meth:`plexosdb.db_solution.PlexosSolution.to_duckdb`.

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

## Declared methods

### is_in_memory

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution_models.py#L35)

```text
is_in_memory(self) -> bool
```

Return *True* when the database lives in memory only.

