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

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L79)

Validate membership records have the exact required fields.

**Parameters**

- `memberships : list[dict[str, int]]`
  Membership dictionaries expected to contain exactly these keys:
  parent_object_id, child_object_id, collection_id, child_class_id,
  parent_class_id.

**Returns**

- `bool`
  True when all records contain exactly the expected keys, otherwise False.

```text
check_memberships_from_records(memberships: list[dict[str, int]]) -> bool
```

#### check_attribute_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L97)

Check if an attribute exists for a specific object.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `attribute_name : str`
  Name of the attribute to validate.
- `object_name : str`
  Name of the target object.
- `object_class : ClassEnum`
  Class for the target object.

**Returns**

- `bool`
  True if the object has an assigned value for the attribute.

```text
check_attribute_exists(db: PlexosDB, attribute_name: str, /, *, object_name: str, object_class: ClassEnum) -> bool
```

#### check_class_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L133)

Check if a class exists in the database.

Determines whether a class with the given enumeration exists in the schema.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `class_enum : ClassEnum`
  Class enumeration to check.

**Returns**

- `bool`
  True if the class exists, False otherwise.

**See Also**

- `PlexosDB.get_class_id` : Get the ID for a class.
- `PlexosDB.list_classes` : List all available classes.

```text
check_class_exists(db: PlexosDB, class_enum: ClassEnum) -> bool
```

#### check_category_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L159)

Check if a category exists for a specific class.

Determines whether a category with the given name exists for the specified
class.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `class_enum : ClassEnum`
  Class enumeration to check the category for.
- `name : str`
  Name of the category to check.

**Returns**

- `bool`
  True if the category exists, False otherwise.

**Raises**

- `NotFoundError`
  If class_enum does not exist in the database. This indicates a
  programming error because categories are class-scoped.

```text
check_category_exists(db: PlexosDB, class_enum: ClassEnum, name: str) -> bool
```

#### check_collection_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L198)

Check if a collection exists in the database.

Determines whether a collection with the given enumeration exists,
optionally filtered by parent and/or child class.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `collection_enum : CollectionEnum`
  Collection enumeration to check.
- `parent_class : ClassEnum | None, optional`
  Parent class enumeration to filter by.
- `child_class : ClassEnum | None, optional`
  Child class enumeration to filter by.

**Returns**

- `bool`
  True if the collection exists (matching all specified criteria),
  False otherwise.

**Raises**

- `NotFoundError`
  If parent_class or child_class is specified but does not exist.

**Notes**

The method returns False only when the collection itself does not exist or
does not match the requested class filter.

```text
check_collection_exists(db: PlexosDB, collection_enum: CollectionEnum, /, *, parent_class: ClassEnum | None=None, child_class: ClassEnum | None=None) -> bool
```

#### check_data_id_exist

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L272)

Check that a data id is present on t_data table.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `data_id : int`
  Data row identifier.

**Returns**

- `bool`
  True when data_id exists in t_data, False otherwise.

```text
check_data_id_exist(db: PlexosDB, data_id: int) -> bool
```

#### check_tag_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L291)

Check if a tag exists linking a data record to an object.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `data_id : int`
  Data ID to check.
- `object_id : int`
  Object ID to check.

**Returns**

- `bool`
  True if a t_tag row exists for the pair (data_id, object_id),
  otherwise False.

```text
check_tag_exists(db: PlexosDB, data_id: int, object_id: int) -> bool
```

#### check_membership_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L313)

Check if a membership exists between two objects.

Determines whether a membership relationship exists between the specified
parent and child objects within the given collection.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `parent_object_name : str`
  Name of the parent object.
- `child_object_name : str`
  Name of the child object.
- `parent_class : ClassEnum`
  Class enumeration of the parent object.
- `child_class : ClassEnum`
  Class enumeration of the child object.
- `collection : CollectionEnum`
  Collection enumeration defining the relationship type.

**Returns**

- `bool`
  True if the membership exists, False otherwise.

**Raises**

- `NotFoundError`
  If parent class, child class, or collection filter is invalid.

```text
check_membership_exists(db: PlexosDB, parent_object_name: str, child_object_name: str, /, *, parent_class: ClassEnum, child_class: ClassEnum, collection: CollectionEnum) -> bool
```

#### check_object_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L391)

Check if an object exists in the database.

Determines whether an object with the given name and class exists,
optionally filtered by category.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `class_enum : ClassEnum`
  Class enumeration of the object.
- `name : str`
  Name of the object to check.
- `category : str | None, optional`
  Category name to filter by.

**Returns**

- `bool`
  True if the object exists (and matches category if specified),
  False otherwise.

**Raises**

- `NotFoundError`
  If class_enum does not exist in the database.

```text
check_object_exists(db: PlexosDB, class_enum: ClassEnum, /, name: str, *, category: str | None=None) -> bool
```

#### check_property_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L444)

Check if properties exist for a specific collection and class.

Verifies that all specified property names are valid for the given
collection and class.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `collection_enum : CollectionEnum`
  Collection enumeration the properties should belong to.
- `object_class : ClassEnum`
  Class enumeration of the object.
- `property_names : str | Iterable[str]`
  Property name or names to check.
- `parent_class : ClassEnum | None, optional`
  Class enumeration of the parent object.

**Returns**

- `bool`
  True if all properties exist, False otherwise.

**Raises**

- `NotFoundError`
  If parent class, child class, or collection filter is invalid.

**Notes**

If any property in the list is invalid, the function returns False and logs
the invalid list.

```text
check_property_exists(db: PlexosDB, collection_enum: CollectionEnum, /, object_class: ClassEnum, property_names: str | Iterable[str], *, parent_class: ClassEnum | None=None) -> bool
```

#### check_scenario_exists

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L528)

Check if a scenario exists in the database.

Determines whether a scenario with the given name exists.

**Parameters**

- `db : PlexosDB`
  Database instance.
- `name : str`
  Name of the scenario to check.

**Returns**

- `bool`
  True if the scenario exists, False otherwise.

**See Also**

- `PlexosDB.get_class_id` : Get the ID for a class.
- `ClassEnum.Scenario` : Scenario class enumeration.

```text
check_scenario_exists(db: PlexosDB, name: str) -> bool
```

#### get_default_schema_columns

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L556)

Return table columns introspected from the packaged PLEXOS schema.

```text
get_default_schema_columns() -> tuple[tuple[str, frozenset[str]], ...]
```

#### validate_value_by_rule

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L1030)

Validate a numeric value using Between, In, or comparison rules.

```text
validate_value_by_rule(value: SQLiteValue, validation_rule: str) -> ValidationResult
```

#### repair_safe_membership_class_ids

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L1244)

Repair membership class IDs when the object and collection agree.

```text
repair_safe_membership_class_ids(db: SQLiteManager, /) -> None
```

#### register_plexosdb_check_methods

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/checks.py#L1346)

Attach check_* instance methods to PlexosDB from this module.

```text
register_plexosdb_check_methods(plexosdb_cls: type[PlexosDB]) -> None
```

<!-- End generated API reference -->
