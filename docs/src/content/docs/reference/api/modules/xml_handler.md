---
title: "XML Handler"
---

<!-- Generated API reference -->

## Public module members

### plexosdb.xml_handler

#### PLEXOS_NAMESPACE

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/xml_handler.py#L14)

```text
PLEXOS_NAMESPACE = 'http://tempuri.org/MasterDataSet.xsd'
```

#### XMLHandler

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/xml_handler.py#L17)

PLEXOS XML handler.

##### Methods and properties

###### parse

```text
parse(cls, fpath: str | PathLike[str], namespace: str=PLEXOS_NAMESPACE, **kwargs: Any) -> 'XMLHandler'
```

Return XML instance from file requested.

###### create_table_element

```text
create_table_element(self, rows: list[tuple[Any, ...]], column_types: dict[str, str], table_name: str) -> bool
```

Create XML elements for a given table.

###### get_records

```text
get_records(self, element_enum: Schema, *elements: Iterable[str | int], rename_dict: dict[str, str] | None=None, **tag_elements: Any) -> list[XMLRecord]
```

Return XML text records without evaluating or coercing their contents.

Values are strings or None for empty elements. Schema-specific conversion
belongs to the importer so numeric-looking text retains its spelling.

###### iter

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

###### to_xml

```text
to_xml(self, fpath: str | PathLike[str]) -> bool
```

Save memory xml to file.

Full reference: [`XMLHandler`](/plexosdb/reference/python-api/xmlhandler/).

#### xml_query

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/xml_handler.py#L275)

Construct XPath query for extracting data from a XML with no namespace.

**Parameters**

- `element_name`
  String that matches the desired element
- `*tags`
  Tag names to filter
- `**kwargs`
  Tag name and value child of the element. (E.g., class_id=2)

**Returns**

- `XPath query string constructed based on the provided conditions.`

**Examples**

A simple example for one condition:

```python
>>> query_string = xml_query("t_object", class_id="2")
>>> print(query_string)
".//t_object[class_id='2']"
```

For multiple condition:

```python
>>> query_string = xml_query("t_object", class_id="2", enum_id="1")
>>> print(query_string)
".//t_object[class_id='2'][enum_id='1']"
```

```text
xml_query(element_name: str, *tags: Any, **tag_elements: Any) -> str
```

<!-- End generated API reference -->
