---
title: "Utilities"
---

<!-- Generated API reference -->

## Public module members

### plexosdb.utils

#### PreparedPropertiesResult

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L25)

Prepared inputs for bulk property insertion.

#### batched

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L35)

Implement batched iterator.

https://docs.python.org/3/library/itertools.html#itertools.batched

```text
batched(iterable: Iterable[Any], n: int) -> Iterator[tuple[Any, ...]]
```

#### validate_string

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L44)

Validate string and convert it to python object.

This function also tries to parse floats or ints. Numeric strings containing
underscores and complex-looking strings are kept unchanged because they may
be PLEXOS identifiers.

**Parameters**

- `value: Any`
  String value to be converted to Python Object

**Note**

The ast is slow due to the multiple cases. Use it only on simple for loops
as this could become a bottleneck.

```text
validate_string(value: str) -> Any
```

#### no_space

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L93)

Collate function for catching strings with spaces.

```text
no_space(a: str, b: str) -> int
```

#### normalize_names

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L102)

Normalize a name or list of names into a unique list of strings.

**Parameters**

- `names : str or Iterable[str]`
  A string or an iterable of strings to normalize

**Returns**

- `list[str]`
  A deduplicated list of the provided names

**Raises**

- `ValueError`
  If the input is neither a string nor an iterable of strings

```text
normalize_names(*args: str | Iterable[str]) -> list[str]
```

#### prepare_sql_data_params

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L128)

Create list of tuples for data ingestion.

**Parameters**

- `records : list[dict[str, float]]`
  List of records where each record is a dictionary containing 'name'
  and property values
- `memberships : list[dict[str, int]]`
  List of membership dictionaries with 'name' and 'membership_id' keys
- `property_mapping : list[tuple[str, int]]`
  List of tuples mapping property names to property IDs

**Returns**

- `list[tuple[int, int, Any]]`
  List of tuples containing (membership_id, property_id, value)
  for database insertion

```text
prepare_sql_data_params(records: list[dict[str, float]], memberships: list[dict[str, Any]], property_mapping: list[tuple[str, int]]) -> list[tuple[int, int, Any]]
```

#### create_membership_record

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L162)

Create membership records for database insertion.

**Parameters**

- `object_ids : Iterable[int]`
  Iterable of child object IDs to create memberships for
- `child_object_class_id : int`
  Class ID for the child objects
- `parent_object_id : int`
  ID of the parent object
- `parent_object_class_id : int`
  Class ID for the parent object
- `collection_id : int`
  ID of the collection to which the membership belongs

**Returns**

- `list[dict[str, int]]`
  List of dictionaries representing membership records ready
  for database insertion

```text
create_membership_record(object_ids: Iterable[int], child_object_class_id: int, parent_object_id: int, parent_object_class_id: int, collection_id: int) -> list[dict[str, int]]
```

#### plan_property_inserts

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L298)

Prepare SQL parameters for property insertion.

```text
plan_property_inserts(db: PlexosDB, records: list[dict[str, Any]], *, object_class: ClassEnum, collection: CollectionEnum, parent_class: ClassEnum) -> PreparedPropertiesResult
```

#### get_system_object_name

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L417)

Return the canonical System object name for this model.

**Parameters**

- `db : PlexosDB`
  Database instance to query.

**Returns**

- `str`
  The name of the System object.

**Raises**

- `NotFoundError`
  If no System object exists in the model.
- `ValueError`
  If multiple System objects exist and none is named "System".

```text
get_system_object_name(db: PlexosDB) -> str
```

#### resolve_membership_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L452)

Resolve a single membership ID for property operations.

**Parameters**

- `db : PlexosDB`
  Database instance to query.
- `object_name : str`
  Name of the child object.
- `object_class : ClassEnum`
  Class of the child object.
- `collection : CollectionEnum`
  Collection defining the membership relationship.
- `parent_class : ClassEnum`
  Class of the parent object.
- `parent_object_name : str | None, optional`
  Explicit parent object name. If provided, uses direct lookup.

**Returns**

- `int`
  The membership ID.

**Raises**

- `NotFoundError`
  If no matching membership is found.
- `ValueError`
  If multiple memberships exist (ambiguous).

```text
resolve_membership_id(db: PlexosDB, object_name: str, *, object_class: ClassEnum, collection: CollectionEnum, parent_class: ClassEnum, parent_object_name: str | None=None) -> int
```

#### insert_property_values

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L577)

Insert property data and return mapping of data IDs to object names.

**Parameters**

- `db : PlexosDB`
  Database instance
- `params : list[tuple]`
  List of (membership_id, property_id, value) tuples
- `metadata_map : dict | None, optional`
  Mapping of params to metadata (band, date_from, date_to), by default None

**Returns**

- `dict`
  Mapping of (membership_id, property_id, value) to (data_id, obj_name)

```text
insert_property_values(db: PlexosDB, params: list[tuple[int, int, Any]], *, metadata_map: dict[tuple[int, int, Any, int], dict[str, Any]] | None=None) -> dict[tuple[int, int, Any, int], tuple[int, str]]
```

#### apply_scenario_tags

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L642)

Insert scenario tags for property data.

**Parameters**

- `db : PlexosDB`
  Database instance
- `params : list[tuple]`
  List of (membership_id, property_id, value) tuples
- `scenario : str`
  Scenario name
- `chunksize : int`
  Number of records to process in each batch

```text
apply_scenario_tags(db: PlexosDB, params: list[tuple[int, int, Any]], /, *, scenario: str, chunksize: int, data_id_map: dict[tuple[int, int, Any, int], tuple[int, str]] | None=None) -> None
```

#### insert_property_texts

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L697)

Add text data for properties from specified field.

**Parameters**

- `db : PlexosDB`
  Database instance
- `params : list[tuple]`
  List of (membership_id, property_id, value) tuples
- `data_id_map : dict`
  Mapping of (membership_id, property_id, value) to (data_id, obj_name)
- `records : list[dict]`
  Original records containing the text field
- `field_name : str`
  Name of the field in records containing text data
- `text_class : ClassEnum`
  ClassEnum for the text data
- `metadata_map : dict | None, optional`
  Metadata map keyed by param tuple to drive property-specific text mapping

```text
insert_property_texts(db: PlexosDB, params: list[tuple[int, int, Any]], /, *, data_id_map: dict[tuple[int, int, Any, int], tuple[int, str]], records: list[dict[str, Any]], field_name: str, text_class: ClassEnum, metadata_map: dict[tuple[int, int, Any, int], dict[str, Any]] | None=None) -> None
```

#### build_data_id_map

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L849)

Build mapping of (membership_id, property_id, value) to (data_id, obj_name).

**Parameters**

- `db_manager : DBManager`
  Database manager instance for executing queries
- `params : list[tuple]`
  List of (membership_id, property_id, value) tuples

**Returns**

- `dict`
  Mapping of (membership_id, property_id, value) to (data_id, obj_name)

```text
build_data_id_map(db: SQLiteManager, params: list[tuple[int, int, Any]]) -> dict[tuple[int, int, Any], tuple[int, str]]
```

#### get_scenario_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/utils.py#L881)

Get or create scenario ID.

**Parameters**

- `db_manager : DBManager`
  Database manager instance
- `scenario : str`
  Scenario name

**Returns**

- `int`
  Scenario object ID

```text
get_scenario_id(db: PlexosDB, scenario: str) -> int
```

<!-- End generated API reference -->
