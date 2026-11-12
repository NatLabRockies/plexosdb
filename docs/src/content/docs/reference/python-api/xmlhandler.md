---
title: "XMLHandler"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/xml_handler.py#L17)

PLEXOS XML handler.

## Import

```python
from plexosdb import XMLHandler
```

## Constructor

```text
__init__(self, fpath: str | PathLike[str] | None=None, namespace: str=PLEXOS_NAMESPACE, in_memory: bool=True, initialize: bool=False) -> None
```

Initialize XML handler for PLEXOS datasets.

**Parameters**

- `fpath : str or PathLike, optional`
  Path to an existing XML file to load.
- `namespace : str, optional`
  XML namespace to use when serializing.
- `in_memory : bool, optional`
  Store element caches in memory for faster lookups.
- `initialize : bool, optional`
  Build an empty XML tree instead of parsing a file.

**Returns**

- `None`

## Declared methods and properties

### parse

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/xml_handler.py#L80)

```text
parse(cls, fpath: str | PathLike[str], namespace: str=PLEXOS_NAMESPACE, **kwargs: Any) -> 'XMLHandler'
```

Return XML instance from file requested.

### create_table_element

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/xml_handler.py#L89)

```text
create_table_element(self, rows: list[tuple[Any, ...]], column_types: dict[str, str], table_name: str) -> bool
```

Create XML elements for a given table.

### get_records

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/xml_handler.py#L121)

```text
get_records(self, element_enum: Schema, *elements: Iterable[str | int], rename_dict: dict[str, str] | None=None, **tag_elements: Any) -> list[XMLRecord]
```

Return XML text records without evaluating or coercing their contents.

Values are strings or None for empty elements. Schema-specific conversion
belongs to the importer so numeric-looking text retains its spelling.

### iter

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/xml_handler.py#L140)

```text
iter(self, element_type: Schema, *elements: Iterable[str | int], label: str | None=None, **tags: Any) -> Iterable[ET.Element]
```

Return elements from the XML based on the type.

This functions serves as a low-level query to the XML file.

**Parameters**

- `element_type`
  Enum of the Schema wanted, e.g., `Schema.Class`, `Schema.Objects`.
- `*elements`
  Sequence of ids, strings, or ints to get.
- `label`
  XML child label to extract. Defaults to `Schema[elementy_type].label`.
- `**tags`
  Additional key: value pairs to match the XML, e.g., `kwargs = {"class_id": 1}`.

**Return**

  XML query match.

### to_xml

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/xml_handler.py#L180)

```text
to_xml(self, fpath: str | PathLike[str]) -> bool
```

Save memory xml to file.
