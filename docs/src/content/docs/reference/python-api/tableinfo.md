---
title: "TableInfo"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/db_solution_models.py#L64)

Metadata about one table or view in a DuckDB solution schema.

## Import

```python
from plexosdb import TableInfo
```

## Declared fields

### name

```text
name: Annotated[str, 'DuckDB table or view name.'] = field(metadata={'description': 'DuckDB table or view name.'})
```

### schema

```text
schema: Annotated[str, 'DuckDB schema containing the table or view.'] = field(metadata={'description': 'DuckDB schema containing the table or view.'})
```

### table_type

```text
table_type: Annotated[str, 'DuckDB information_schema table type.'] = field(metadata={'description': 'DuckDB information_schema table type.'})
```

## Declared methods
