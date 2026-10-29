---
title: "PlexosDB"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L110)

High-level API for PlexosDB schema manipulation.

## Import

```python
from plexosdb import PlexosDB
```

## Constructor

```text
__init__(self, fpath_or_conn: Path | str | sqlite3.Connection | None=None, new_db: bool=False, **kwargs: Any) -> None
```

## Declared methods

### version

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L137)

```text
version(self) -> tuple[int, ...] | None
```

Get the PLEXOS version of the loaded model.

### from_xml

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L231)

```text
from_xml(cls, xml_path: str | Path, schema: str | None=None, **kwargs: Any) -> 'PlexosDB'
```

Construct a PlexosDB instance from an XML file.

### add_attribute

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L315)

```text
add_attribute(self, object_class: ClassEnum, /, object_name: str, *, attribute_name: str, attribute_value: str | float | int) -> int
```

Add attribute to a given object.

### add_band

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L356)

```text
add_band(self, data_id: int, band_id: int, /, *, state: int | None=None) -> None
```

Add a band to a property data record.

### add_category

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L383)

```text
add_category(self, class_enum: ClassEnum, /, name: str) -> int
```

Add a new category for a given class.

### add_custom_column

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L434)

```text
add_custom_column(self, class_enum: ClassEnum, name: str, /, *, position: int | None=None) -> int
```

Add a custom column to a class.

### add_datafile_tag

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L445)

```text
add_datafile_tag(self, data_id: int, file_path: str, /, *, description: str | None=None) -> int
```

Add a Data File tag to a property data record.

### add_membership

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L503)

```text
add_membership(self, parent_class_enum: ClassEnum, child_class_enum: ClassEnum, parent_object_name: str, child_object_name: str, collection_enum: CollectionEnum) -> int
```

Add a membership between two objects for a given collection.

### add_memberships_from_records

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L573)

```text
add_memberships_from_records(self, records: list[dict[str, int]], /, *, chunksize: int=10000) -> bool
```

Bulk insert multiple memberships from a list of records.

### add_metadata

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L697)

```text
add_metadata(self, entity_type: Literal['object', 'membership', 'data'], entity_id: int, class_name: str, property_name: str, value: str, /, *, state: int | None=None) -> None
```

Add metadata to an entity (object, membership, or data).

### add_object

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L711)

```text
add_object(self, class_enum: ClassEnum, /, name: str, *, description: str | None=None, category: str | None=None, collection_enum: CollectionEnum | Literal[False] | None=None) -> int
```

Add an object to the database and append a system membership.

### add_objects

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L798)

```text
add_objects(self, class_enum: ClassEnum, *object_names: str, category: str | None=None) -> None
```

Add multiple objects of the same class to the database in bulk.

### add_properties_from_records

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L871)

```text
add_properties_from_records(self, records: list[dict[str, Any]], /, *, object_class: ClassEnum, parent_class: ClassEnum=ClassEnum.System, collection: CollectionEnum, scenario: str, chunksize: int=10000) -> None
```

Bulk insert multiple properties from a list of records, with optional text data.

### add_attributes_from_records

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1021)

```text
add_attributes_from_records(self, records: list[dict[str, Any]], /, *, object_class: ClassEnum, chunksize: int=10000) -> None
```

Bulk insert attribute values for objects.

### add_property

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1235)

```text
add_property(self, object_class_enum: ClassEnum, /, object_name: str, name: str, value: str | int | float, *, scenario: str | None=None, band: int | None=None, date_from: datetime | None=None, date_to: datetime | None=None, datafile_text: str | None=None, timeslice: str | None=None, collection_enum: CollectionEnum | None=None, parent_class_enum: ClassEnum | None=None, parent_object_name: str | None=None) -> int
```

Add a property for a given object in the database.

### add_scenario

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1360)

```text
add_scenario(self, name: str, category: str | None=None) -> int
```

Add a scenario object in the database.

### add_report

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1392)

```text
add_report(self, /, *, object_name: str, property: str, collection: CollectionEnum, parent_class: ClassEnum, child_class: ClassEnum, phase_id: int=4, report_period: bool | None=None, report_summary: bool | None=True, report_statistics: bool | None=None, report_samples: bool | None=None, write_flat_files: bool=False) -> None
```

Add an output property configuration to an existing report.

### add_text

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1508)

```text
add_text(self, text_class: ClassEnum, text_value: str | int | float, data_id: int) -> int
```

Add text data to a property data record.

### add_time_slice

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1539)

```text
add_time_slice(self, name: str, /, *, interval: str, start_datetime: str, end_datetime: str, description: str | None=None) -> int
```

Add a time slice definition to the database.

### add_variable_tag

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1552)

```text
add_variable_tag(self, data_id: int, variable_name: str, /, *, value: str | float | None=None) -> int
```

Add a Variable tag to a property data record.

### backup_database

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1563)

```text
backup_database(self, target_path: str | Path) -> None
```

Backup the in-memory database to a file.

### copy_object

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1567)

```text
copy_object(self, object_class: ClassEnum, original_object_name: str, new_object_name: str, copy_properties: bool=True, copy_attributes: bool=True) -> int
```

Copy an object and its memberships, attributes, properties, tags and texts.

### copy_object_memberships

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1612)

```text
copy_object_memberships(self, object_class: ClassEnum, original_name: str, new_name: str) -> dict[int, int]
```

Copy all existing memberships of old object to the new object.

### create_object_scenario

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1779)

```text
create_object_scenario(self, object_name: str, scenario_name: str, properties: dict[str, Any], /, *, object_class: ClassEnum, description: str | None=None, collection: CollectionEnum | None=None, parent_class: ClassEnum | None=None, base_scenario: str | None=None) -> int
```

Create a new scenario with specific property values for an object.

### create_schema

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1902)

```text
create_schema(self, schema: str | None=None, *, seed_defaults: bool=False, version: int | str | tuple[int, ...] | None=None) -> bool
```

Create database schema from SQL script.

### delete_attribute

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L1999)

```text
delete_attribute(self, attribute_name: str, /, *, object_name: str, object_class: ClassEnum) -> None
```

Delete an attribute value from an object.

### delete_category

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2064)

```text
delete_category(self, category: str, /, *, class_name: ClassEnum) -> None
```

Delete a category from the database.

### delete_membership

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2068)

```text
delete_membership(self, parent_object_name: str, child_object_name: str, /, *, parent_class: ClassEnum, child_class: ClassEnum, collection: CollectionEnum) -> None
```

Delete a membership between two objects.

### delete_metadata

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2081)

```text
delete_metadata(self, entity_type: Literal['object', 'membership', 'data'], entity_id: int, class_name: str, property_name: str) -> None
```

Delete metadata from an entity.

### delete_object

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2091)

```text
delete_object(self, class_enum: ClassEnum, /, *, name: str) -> None
```

Delete an object and its memberships from the database.

### delete_property

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2104)

```text
delete_property(self, object_class: ClassEnum, object_name: str, /, *, property_name: str, collection: CollectionEnum | None=None, parent_class: ClassEnum | None=None, parent_object_name: str | None=None, scenario: str | None=None) -> None
```

Delete a property from an object.

### delete_text

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2222)

```text
delete_text(self, data_id: int, /, *, class_id: int) -> None
```

Delete text data from a property data record.

### get_attribute

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2232)

```text
get_attribute(self, object_class: ClassEnum, /, *, object_name: str, attribute_name: str) -> Any
```

Get an assigned attribute value for a specific object.

### get_attribute_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2257)

```text
get_attribute_id(self, class_enum: ClassEnum, /, name: str) -> int
```

Return the ID for a given attribute.

### get_attributes

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2296)

```text
get_attributes(self, object_name: str, /, *, object_class: ClassEnum, attribute_names: str | Iterable[str] | None=None) -> list[dict[str, Any]]
```

Retrieve assigned attribute values for a specific object.

### get_category_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2364)

```text
get_category_id(self, class_enum: ClassEnum, /, name: str) -> int
```

Return the ID for a given category.

### get_category_max_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2416)

```text
get_category_max_id(self, class_enum: ClassEnum) -> int
```

Return the current maximum rank for a given category class.

### get_class_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2464)

```text
get_class_id(self, class_enum: ClassEnum) -> int
```

Return the ID for a given class.

### get_collection_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2500)

```text
get_collection_id(self, collection: CollectionEnum, /, parent_class_enum: ClassEnum, child_class_enum: ClassEnum) -> int
```

Return the ID for a given collection.

### get_config

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2558)

```text
get_config(self, element: str | None=None) -> dict[str, Any] | list[dict[str, Any]]
```

Get configuration values from the database.

### get_custom_columns

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2562)

```text
get_custom_columns(self, class_enum: ClassEnum | None=None) -> list[dict[str, Any]]
```

Get custom columns, optionally filtered by class.

### get_membership_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2566)

```text
get_membership_id(self, /, parent_name: str, child_name: str, collection: CollectionEnum) -> int
```

Return the ID for a given membership.

### list_object_memberships

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2629)

```text
list_object_memberships(self, class_enum: ClassEnum, /, name: str, category: str | None=None, collection: CollectionEnum | None=None, exclude_system_membership: bool=False) -> list[dict[str, Any]]
```

Retrieve all memberships for a given object.

### get_memberships_system

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2710)

```text
get_memberships_system(self, *object_names: Iterable[str] | str, object_class: ClassEnum, collection: CollectionEnum | None=None) -> list[dict[str, Any]]
```

Retrieve memberships for the requested object names.

### get_metadata

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2779)

```text
get_metadata(self, entity_type: Literal['object', 'membership', 'data'], entity_id: int, /, *, class_name: str | None=None, property_name: str | None=None) -> list[dict[str, Any]]
```

Retrieve metadata for an entity.

### get_object_data_ids

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2791)

```text
get_object_data_ids(self, class_enum: ClassEnum, /, name: str, property_names: str | Iterable[str] | None=None, *, parent_class_enum: ClassEnum=ClassEnum.System, collection_enum: CollectionEnum | None=None, category: str | None=None) -> list[int]
```

Get all the data_id values for a given object in the database.

### get_object_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2897)

```text
get_object_properties(self, class_enum: ClassEnum, /, name: str, property_names: str | Iterable[str] | None=None, *, parent_class_enum: ClassEnum | None=None, collection_enum: CollectionEnum | None=None, category: str | None=None, scenario: str | Iterable[str] | None=None, scenario_category: str | Iterable[str] | None=None) -> list[PropertyRecord]
```

Retrieve properties for a specific object.

### get_object_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L2993)

```text
get_object_id(self, class_enum: ClassEnum, /, name: str, *, category: str | None=None) -> int
```

Return the ID for a given object.

### get_objects_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3058)

```text
get_objects_id(self, *object_names: Iterable[str] | str, class_enum: ClassEnum) -> list[int]
```

Get object_ids for a list of names for a given class.

### get_plexos_version

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3080)

```text
get_plexos_version(self) -> tuple[int, ...] | None
```

Return the version information of the PLEXOS model.

### get_property_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3084)

```text
get_property_id(self, property_name: str, /, *, collection_enum: CollectionEnum, child_class_enum: ClassEnum, parent_class_enum: ClassEnum | None=None) -> int
```

Return the ID for a given property.

### get_property_unit

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3146)

```text
get_property_unit(self, property_name: str, /, collection_enum: CollectionEnum, parent_class_enum: ClassEnum, child_class_enum: ClassEnum) -> str
```

Get the unit for a specific property.

### get_scenario_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3157)

```text
get_scenario_id(self, name: str) -> int
```

Return the ID for a given scenario.

### get_text

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3189)

```text
get_text(self, data_id: int, /, *, class_id: int | None=None) -> list[dict[str, Any]]
```

Retrieve text data associated with a property data record.

### get_unit

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3199)

```text
get_unit(self, unit_id: int) -> dict[str, Any]
```

Get details for a specific unit.

### has_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3203)

```text
has_properties(self, class_enum: ClassEnum, /, name: str, *, collection_enum: CollectionEnum | None=None, category: str | None=None) -> bool
```

Check if the given object has any properties associated with it.

### import_from_csv

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3280)

```text
import_from_csv(self, source_path: str | Path, /, *, tables: list[str] | None=None) -> None
```

Import data from CSV files into the database.

### iterate_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3284)

```text
iterate_properties(self, /, *, class_enum: ClassEnum | None=None, object_names: str | Iterable[str] | None=None, property_names: str | Iterable[str] | None=None, parent_class: ClassEnum | None=None, collection: CollectionEnum | None=None, category: str | None=None, scenario: str | Iterable[str] | None=None, scenario_category: str | Iterable[str] | None=None, batch_size: int=1000) -> Iterator[PropertyRecord]
```

Iterate through properties with chunked processing to handle large datasets efficiently.

### list_attributes

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3409)

```text
list_attributes(self, class_enum: ClassEnum) -> list[str]
```

Get all attributes for a specific class.

### list_categories

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3443)

```text
list_categories(self, class_enum: ClassEnum) -> list[str]
```

Get all categories for a specific class.

### list_child_objects

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3491)

```text
list_child_objects(self, object_name: str, /, *, parent_class: ClassEnum, child_class: ClassEnum | None=None, collection: CollectionEnum | None=None) -> list[dict[str, Any]]
```

List all child objects for a given parent object.

### list_classes

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3608)

```text
list_classes(self) -> list[str]
```

Return all classes names in the database.

### list_collections

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3637)

```text
list_collections(self, /, *, parent_class: ClassEnum | None=None, child_class: ClassEnum | None=None) -> list[dict[str, Any]]
```

List all available collections in the database.

### list_objects_by_class

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3686)

```text
list_objects_by_class(self, class_enum: ClassEnum, /, *, category: str | None=None) -> list[str]
```

Return all objects of a specific class.

### list_parent_objects

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3761)

```text
list_parent_objects(self, object_name: str, /, *, child_class: ClassEnum, parent_class: ClassEnum | None=None, collection: CollectionEnum | None=None) -> list[dict[str, Any]]
```

List all parent objects for a given child object.

### list_reports

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3875)

```text
list_reports(self) -> list[dict[str, Any]]
```

List all defined reports in the database.

### list_scenarios

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3879)

```text
list_scenarios(self) -> list[str]
```

Return all scenarios in the database.

### list_models

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3923)

```text
list_models(self) -> list[str]
```

Return all models in the database.

### list_scenarios_by_model

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L3960)

```text
list_scenarios_by_model(self, model_name: str) -> list[str]
```

List all scenarios associated with a given model.

### list_units

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4000)

```text
list_units(self) -> list[dict[int, str]]
```

List all available units in the database.

### list_valid_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4007)

```text
list_valid_properties(self, collection_enum: CollectionEnum, /, parent_class_enum: ClassEnum, child_class_enum: ClassEnum) -> list[str]
```

Return list of valid property names for a collection.

### list_valid_properties_report

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4062)

```text
list_valid_properties_report(self, collection_enum: CollectionEnum, /, parent_class_enum: ClassEnum, child_class_enum: ClassEnum) -> list[str]
```

Return list of valid property names for reports.

### query

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4105)

```text
query(self, query_string: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[Any]
```

Execute a read-only query and return all results.

### set_config

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4146)

```text
set_config(self, element: str, value: str) -> None
```

Set a configuration value in the database.

### set_date_range

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4150)

```text
set_date_range(self, data_id: int, /, *, date_from: str | None=None, date_to: str | None=None) -> None
```

Set the date range for a property data record.

### to_csv

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4161)

```text
to_csv(self, target_path: str | Path, /, *, tables: list[str] | None=None) -> None
```

Export selected tables or the entire database to CSV files.

### to_xml

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4165)

```text
to_xml(self, target_path: str | Path) -> bool
```

Convert SQLite to XML format.

### update_attribute

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4241)

```text
update_attribute(self, attribute_name: str, new_value: str | float | int, /, *, object_name: str, object_class: ClassEnum) -> None
```

Update an attribute value for an object.

### update_category

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4253)

```text
update_category(self, category: str, new_name: str, /, *, class_name: ClassEnum) -> None
```

Update a category name.

### update_object

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4257)

```text
update_object(self, class_enum: ClassEnum, object_name: str, *, new_name: str, new_category: str | None=None, new_description: str | None=None) -> bool
```

Update an object's attributes.

### update_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4337)

```text
update_properties(self, updates: list[dict[str, Any]]) -> None
```

Update multiple matching property data records in one transaction.

### update_property

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4643)

```text
update_property(self, object_name: str, property_name: str, new_value: str | None, /, *, object_class: ClassEnum, scenario: str | None=None, band: str | int | None=None, collection: CollectionEnum | None=None, parent_class: ClassEnum | None=None, parent_object_name: str | None=None) -> None
```

Update exactly one existing property data record.

### update_scenario

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4793)

```text
update_scenario(self, scenario_name: str, /, *, new_name: str | None=None, new_category: str | None=None, new_description: str | None=None) -> None
```

Update a scenario's properties.

### update_text

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4805)

```text
update_text(self, data_id: int, text_value: str, /, *, class_id: int) -> None
```

Update text data for a property data record.

### validate_value_by_rule

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4817)

```text
validate_value_by_rule(value: SQLiteValue, validation_rule: str) -> ValidationResult
```

Validate a numeric value against a PLEXOS validation rule.

### validate_database

[Source](https://github.com/NatLabRockies/plexosdb/blob/73e7fabe5e9f951231b6120c139cec1e52d12463/src/plexosdb/db.py#L4835)

```text
validate_database(self, /, *, fix_issues: bool=False) -> bool
```

Validate the packaged PLEXOS schema and database relationships.

