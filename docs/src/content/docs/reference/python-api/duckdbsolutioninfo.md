---
title: "DuckDBSolutionInfo"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution_models.py#L41)

Metadata about a DuckDB-backed PLEXOS solution.

## Import

```python
from plexosdb import DuckDBSolutionInfo
```

## Declared fields

### database

```text
database: Annotated[Path | None, 'Filesystem path of the DuckDB file, or None for an in-memory database.'] = field(metadata={'description': 'Filesystem path of the DuckDB file, or None for an in-memory database.'})
```

### source

```text
source: Annotated[Path | None, 'Path to the original PLEXOS solution source, when known.'] = field(metadata={'description': 'Path to the original PLEXOS solution source, when known.'})
```

### model_name

```text
model_name: Annotated[str | None, 'PLEXOS model name recorded by plexos2duckdb.'] = field(default=None, metadata={'description': 'PLEXOS model name recorded by plexos2duckdb.'})
```

### converter_version

```text
converter_version: Annotated[str | None, 'plexos2duckdb converter version.'] = field(default=None, metadata={'description': 'plexos2duckdb converter version.'})
```

## Declared methods

