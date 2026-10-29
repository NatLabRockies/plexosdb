---
title: "ResultTable"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db_solution_models.py#L79)

Metadata for one PLEXOS solution result table or view.

## Import

```python
from plexosdb import ResultTable
```

## Declared fields

### name

```text
name: Annotated[str, 'DuckDB table or view name.'] = field(metadata={'description': 'DuckDB table or view name.'})
```

### schema

```text
schema: Annotated[ResultSchema, 'DuckDB schema containing the result.'] = field(metadata={'description': 'DuckDB schema containing the result.'})
```

### phase

```text
phase: Annotated[PhaseEnum, 'PLEXOS solve phase.'] = field(metadata={'description': 'PLEXOS solve phase.'})
```

### period

```text
period: Annotated[PeriodEnum, 'PLEXOS result period.'] = field(metadata={'description': 'PLEXOS result period.'})
```

### class_enum

```text
class_enum: Annotated[ClassEnum | None, 'Object class associated with the result collection.'] = field(metadata={'description': 'Object class associated with the result collection.'})
```

### collection

```text
collection: Annotated[CollectionEnum, 'PLEXOS collection represented by the result.'] = field(metadata={'description': 'PLEXOS collection represented by the result.'})
```

### property_name

```text
property_name: Annotated[str, 'PLEXOS property represented by the result.'] = field(metadata={'description': 'PLEXOS property represented by the result.'})
```

### table_type

```text
table_type: Annotated[TableTypeEnum, 'DuckDB information_schema table type.'] = field(metadata={'description': 'DuckDB information_schema table type.'})
```

### value_column

```text
value_column: Annotated[str, 'Column containing the result values.'] = field(metadata={'description': 'Column containing the result values.'})
```

## Declared methods

