---
title: "Checks"
---

Validation helpers for checking classes, objects, collections, memberships,
properties, attributes, scenarios, data records, and tags in a `PlexosDB`
database.

For whole-database validation and text reports, see
[Validating a Database](/plexosdb/how-to/validate_database/). Use the public
`PlexosDB.validate_database()` entry point; `_find_*` functions are internal
helpers that consume a `SQLiteManager`.


The existence-check helpers accept a `PlexosDB` instance as their first
argument. The same checks are also available as convenience methods on
`PlexosDB` where the class exposes them.

<!-- Generated API reference -->

## Public module members

### plexosdb.checks

#### check_memberships_from_records

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L79)

Validate membership records have the exact required fields.

```text
check_memberships_from_records(memberships: list[dict[str, int]]) -> bool
```

#### check_attribute_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L97)

Check if an attribute exists for a specific object.

```text
check_attribute_exists(db: PlexosDB, attribute_name: str, /, *, object_name: str, object_class: ClassEnum) -> bool
```

#### check_class_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L133)

Check if a class exists in the database.

```text
check_class_exists(db: PlexosDB, class_enum: ClassEnum) -> bool
```

#### check_category_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L159)

Check if a category exists for a specific class.

```text
check_category_exists(db: PlexosDB, class_enum: ClassEnum, name: str) -> bool
```

#### check_collection_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L198)

Check if a collection exists in the database.

```text
check_collection_exists(db: PlexosDB, collection_enum: CollectionEnum, /, *, parent_class: ClassEnum | None=None, child_class: ClassEnum | None=None) -> bool
```

#### check_data_id_exist

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L272)

Check that a data id is present on t_data table.

```text
check_data_id_exist(db: PlexosDB, data_id: int) -> bool
```

#### check_tag_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L291)

Check if a tag exists linking a data record to an object.

```text
check_tag_exists(db: PlexosDB, data_id: int, object_id: int) -> bool
```

#### check_membership_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L313)

Check if a membership exists between two objects.

```text
check_membership_exists(db: PlexosDB, parent_object_name: str, child_object_name: str, /, *, parent_class: ClassEnum, child_class: ClassEnum, collection: CollectionEnum) -> bool
```

#### check_object_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L391)

Check if an object exists in the database.

```text
check_object_exists(db: PlexosDB, class_enum: ClassEnum, /, name: str, *, category: str | None=None) -> bool
```

#### check_property_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L444)

Check if properties exist for a specific collection and class.

```text
check_property_exists(db: PlexosDB, collection_enum: CollectionEnum, /, object_class: ClassEnum, property_names: str | Iterable[str], *, parent_class: ClassEnum | None=None) -> bool
```

#### check_scenario_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L528)

Check if a scenario exists in the database.

```text
check_scenario_exists(db: PlexosDB, name: str) -> bool
```

#### get_default_schema_columns

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L556)

Return table columns introspected from the packaged PLEXOS schema.

```text
get_default_schema_columns() -> tuple[tuple[str, frozenset[str]], ...]
```

#### validate_value_by_rule

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L1030)

Validate a numeric value using Between, In, or comparison rules.

```text
validate_value_by_rule(value: SQLiteValue, validation_rule: str) -> ValidationResult
```

#### repair_safe_membership_class_ids

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L1244)

Repair membership class IDs when the object and collection agree.

```text
repair_safe_membership_class_ids(db: SQLiteManager, /) -> None
```

#### register_plexosdb_check_methods

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/checks.py#L1346)

Attach check_* instance methods to PlexosDB from this module.

```text
register_plexosdb_check_methods(plexosdb_cls: type[PlexosDB]) -> None
```

<!-- End generated API reference -->
