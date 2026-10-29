---
title: "XML Handler"
---

<!-- Generated API reference -->

## Public module members

### plexosdb.xml_handler

#### PLEXOS_NAMESPACE

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/xml_handler.py#L14)

```text
PLEXOS_NAMESPACE = 'http://tempuri.org/MasterDataSet.xsd'
```

#### XMLHandler

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/xml_handler.py#L17)

PLEXOS XML handler.

##### Methods

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

###### iter

```text
iter(self, element_type: Schema, *elements: Iterable[str | int], label: str | None=None, **tags: Any) -> Iterable[ET.Element]
```

Return elements from the XML based on the type.

###### to_xml

```text
to_xml(self, fpath: str | PathLike[str]) -> bool
```

Save memory xml to file.

Full reference: [`XMLHandler`](/plexosdb/reference/python-api/xmlhandler/).

#### xml_query

[Source](https://github.com/NatLabRockies/plexosdb/blob/783cbe719e0b53a41cf7731131ad55dd171c274a/src/plexosdb/xml_handler.py#L275)

Construct XPath query for extracting data from a XML with no namespace.

```text
xml_query(element_name: str, *tags: Any, **tag_elements: Any) -> str
```

<!-- End generated API reference -->
