---
title: "XMLHandler"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/xml_handler.py#L17)

PLEXOS XML handler.

## Import

```python
from plexosdb import XMLHandler
```

## Constructor

```text
__init__(self, fpath: str | PathLike[str] | None=None, namespace: str=PLEXOS_NAMESPACE, in_memory: bool=True, initialize: bool=False) -> None
```

## Declared methods

### parse

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/xml_handler.py#L80)

```text
parse(cls, fpath: str | PathLike[str], namespace: str=PLEXOS_NAMESPACE, **kwargs: Any) -> 'XMLHandler'
```

Return XML instance from file requested.

### create_table_element

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/xml_handler.py#L89)

```text
create_table_element(self, rows: list[tuple[Any, ...]], column_types: dict[str, str], table_name: str) -> bool
```

Create XML elements for a given table.

### get_records

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/xml_handler.py#L121)

```text
get_records(self, element_enum: Schema, *elements: Iterable[str | int], rename_dict: dict[str, str] | None=None, **tag_elements: Any) -> list[XMLRecord]
```

Return XML text records without evaluating or coercing their contents.

### iter

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/xml_handler.py#L140)

```text
iter(self, element_type: Schema, *elements: Iterable[str | int], label: str | None=None, **tags: Any) -> Iterable[ET.Element]
```

Return elements from the XML based on the type.

### to_xml

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/xml_handler.py#L180)

```text
to_xml(self, fpath: str | PathLike[str]) -> bool
```

Save memory xml to file.

