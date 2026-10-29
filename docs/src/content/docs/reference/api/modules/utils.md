---
title: "Utilities"
---

<!-- Generated API reference -->

## Public module members

### plexosdb.utils

#### PreparedPropertiesResult

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L25)

Prepared inputs for bulk property insertion.

#### batched

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L35)

Implement batched iterator.

```text
batched(iterable: Iterable[Any], n: int) -> Iterator[tuple[Any, ...]]
```

#### validate_string

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L44)

Validate string and convert it to python object.

```text
validate_string(value: str) -> Any
```

#### no_space

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L93)

Collate function for catching strings with spaces.

```text
no_space(a: str, b: str) -> int
```

#### normalize_names

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L102)

Normalize a name or list of names into a unique list of strings.

```text
normalize_names(*args: str | Iterable[str]) -> list[str]
```

#### prepare_sql_data_params

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L128)

Create list of tuples for data ingestion.

```text
prepare_sql_data_params(records: list[dict[str, float]], memberships: list[dict[str, Any]], property_mapping: list[tuple[str, int]]) -> list[tuple[int, int, Any]]
```

#### create_membership_record

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L162)

Create membership records for database insertion.

```text
create_membership_record(object_ids: Iterable[int], child_object_class_id: int, parent_object_id: int, parent_object_class_id: int, collection_id: int) -> list[dict[str, int]]
```

#### plan_property_inserts

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L298)

Prepare SQL parameters for property insertion.

```text
plan_property_inserts(db: PlexosDB, records: list[dict[str, Any]], *, object_class: ClassEnum, collection: CollectionEnum, parent_class: ClassEnum) -> PreparedPropertiesResult
```

#### get_system_object_name

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L417)

Return the canonical System object name for this model.

```text
get_system_object_name(db: PlexosDB) -> str
```

#### resolve_membership_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L452)

Resolve a single membership ID for property operations.

```text
resolve_membership_id(db: PlexosDB, object_name: str, *, object_class: ClassEnum, collection: CollectionEnum, parent_class: ClassEnum, parent_object_name: str | None=None) -> int
```

#### insert_property_values

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L577)

Insert property data and return mapping of data IDs to object names.

```text
insert_property_values(db: PlexosDB, params: list[tuple[int, int, Any]], *, metadata_map: dict[tuple[int, int, Any, int], dict[str, Any]] | None=None) -> dict[tuple[int, int, Any, int], tuple[int, str]]
```

#### apply_scenario_tags

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L642)

Insert scenario tags for property data.

```text
apply_scenario_tags(db: PlexosDB, params: list[tuple[int, int, Any]], /, *, scenario: str, chunksize: int, data_id_map: dict[tuple[int, int, Any, int], tuple[int, str]] | None=None) -> None
```

#### insert_property_texts

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L697)

Add text data for properties from specified field.

```text
insert_property_texts(db: PlexosDB, params: list[tuple[int, int, Any]], /, *, data_id_map: dict[tuple[int, int, Any, int], tuple[int, str]], records: list[dict[str, Any]], field_name: str, text_class: ClassEnum, metadata_map: dict[tuple[int, int, Any, int], dict[str, Any]] | None=None) -> None
```

#### build_data_id_map

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L849)

Build mapping of (membership_id, property_id, value) to (data_id, obj_name).

```text
build_data_id_map(db: SQLiteManager, params: list[tuple[int, int, Any]]) -> dict[tuple[int, int, Any], tuple[int, str]]
```

#### get_scenario_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/utils.py#L881)

Get or create scenario ID.

```text
get_scenario_id(db: PlexosDB, scenario: str) -> int
```

<!-- End generated API reference -->
