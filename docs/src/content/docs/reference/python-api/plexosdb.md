---
title: "PlexosDB"
editUrl: false
---

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L110)

High-level API for PlexosDB schema manipulation.

## Import

```python
from plexosdb import PlexosDB
```

## Constructor

```text
__init__(self, fpath_or_conn: Path | str | sqlite3.Connection | None=None, new_db: bool=False, **kwargs: Any) -> None
```

Initialize the API using an XML file or other data sources.

**Parameters**

- `xml_fname : str | None`
  The XML filename to ingest data from. If None, uses in-memory DB.
- `**kwargs : dict`
  Additional keyword arguments for the backend.

## Declared methods and properties

### version

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L137)

```text
version: tuple[int, ...] | None
```

Get the PLEXOS version of the loaded model.

### from_xml

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L231)

```text
from_xml(cls, xml_path: str | Path, schema: str | None=None, **kwargs: Any) -> 'PlexosDB'
```

Construct a PlexosDB instance from an XML file.

This factory method creates a new PlexosDB instance and populates it with data
from the provided XML file. It creates the database schema and processes all
valid XML elements into their corresponding database tables.

**Parameters**

- `xml_path : str | Path`
  Path to the XML file to import data from
- `schema: str | None`
  SQL schema to initialize the database
- `**kwargs : dict`
  Additional keyword arguments to pass to the PlexosDB constructor

**Returns**

- `PlexosDB`
  A new PlexosDB instance initialized with data from the XML file

**Raises**

- `FileNotFoundError`
  If the specified XML file does not exist

**See Also**

- `PlexosDB` : PLEXOS SQLite manager
- `create_schema` : Creates the database schema
- `XMLHandler.parse` : Parses the XML file
- `str2enum` : Converts XML tag names to schema enumerations

**Notes**

XML text is bound without Python literal evaluation. Text columns preserve
their XML content; numeric columns use SQLite's affinity and precision
rules. In particular, integers outside SQLite's signed 64-bit range may
be stored as REAL and lose precision. Boolean words are converted to 0/1
only for columns declared as BIT. Empty XML elements bind as NULL.

This method groups records by their column structure to handle varying record
formats in the XML data. Each group of records with consistent structure is
processed separately to avoid SQL errors from column mismatches.

This constructor assumes we are creating a new database. If you want to add
data to an existing database, you should use other methods.

**Examples**

```python
>>> db = PlexosDB.from_xml("model.xml")
>>> print(db.version)
'8.3.0'
```

### add_attribute

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L315)

```text
add_attribute(self, object_class: ClassEnum, /, object_name: str, *, attribute_name: str, attribute_value: str | float | int) -> int
```

Add attribute to a given object.

Attributes are different from properties. They live on a separate table
and are mostly used for model configuration.

**Parameters**

- `object_class`
  ClassEnum from the object to be added. E.g., for generators class_id=ClassEnum.Generators
- `object_name : str`
  Name to be added to the object
- `attribute_name`
  Valid name of the attribute to be added for the given class
- `attribute_value`
  Value to be added to the attribute

**Returns**

- `int`
  attribute_id

### add_band

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L356)

```text
add_band(self, data_id: int, band_id: int, /, *, state: int | None=None) -> None
```

Add a band to a property data record.

**Parameters**

- `data_id : int`
  ID of the data record to add the band to
- `band_id : int`
  ID of the band to add
- `state : int | None, optional`
  State value, by default None

### add_category

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L383)

```text
add_category(self, class_enum: ClassEnum, /, name: str) -> int
```

Add a new category for a given class.

Creates a new category for the specified class. If the category already exists,
it returns the ID of the existing category.

**Parameters**

- `class_name : ClassEnum`
  Class enumeration for the category, e.g., for generators use ClassEnum.Generator
- `name : str`
  Name of the category to be added

**Returns**

- `int`
  The ID of the created or existing category

**See Also**

- `check_category_exists` : Check if a category exists for a specific class
- `get_category_id` : Get the ID for an existing category
- `get_category_max_id` : Get the maximum rank ID for a class's categories
- `get_class_id` : Get the ID for a class

**Notes**

The database schema does not enforce uniqueness on the `class_id`, which means
multiple categories with the same name can exist for different classes. The category's
unique identifier is automatically handled by the database.

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_category("mycategory", ClassEnum.Generator)
1
```

### add_custom_column

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L434)

```text
add_custom_column(self, class_enum: ClassEnum, name: str, /, *, position: int | None=None) -> int
```

Add a custom column to a class.

### add_datafile_tag

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L445)

```text
add_datafile_tag(self, data_id: int, file_path: str, /, *, description: str | None=None) -> int
```

Add a Data File tag to a property data record.

Creates a link between a property data record and a DataFile object
by finding the DataFile object that has a Filename property matching
the provided file path.

**Parameters**

- `data_id : int`
  The data ID of the property to tag
- `file_path : str`
  The file path to link to, must match a DataFile's Filename property
- `description : str, optional`
  Optional description for the tag (currently unused)

**Returns**

- `int`
  The data_id that was tagged

**Raises**

- `ValueError`
  If no DataFile with the matching file path is found

### add_membership

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L503)

```text
add_membership(self, parent_class_enum: ClassEnum, child_class_enum: ClassEnum, parent_object_name: str, child_object_name: str, collection_enum: CollectionEnum) -> int
```

Add a membership between two objects for a given collection.

Creates a relationship between parent and child objects within the specified collection.

**Parameters**

- `parent_class_enum : ClassEnum`
  Class enumeration of the parent object
- `child_class_enum : ClassEnum`
  Class enumeration of the child object
- `parent_object_name : str`
  Name of the parent object
- `child_object_name : str`
  Name of the child object
- `collection_enum : CollectionEnum`
  Collection enumeration defining the relationship type

**Returns**

- `int`
  ID of the created membership

**See Also**

- `get_class_id` : Get the ID for a class
- `get_object_id` : Get the ID for an object
- `get_collection_id` : Get the ID for a collection
- `get_membership_id` : Get the ID for an existing membership

**Notes**

This method establishes relationships between objects in the PLEXOS model.
The database enforces uniqueness for parent-child-collection combinations.

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Region, "Parent")
>>> db.add_object(ClassEnum.Node, "Child")
>>> db.add_membership(ClassEnum.Region, ClassEnum.Node, "Parent", "Child")
1
```

### add_memberships_from_records

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L573)

```text
add_memberships_from_records(self, records: list[dict[str, int]], /, *, chunksize: int=10000) -> bool
```

Bulk insert multiple memberships from a list of records.

Efficiently adds multiple membership relationships between objects in batches.
This method is much more efficient than calling `add_membership` multiple times.

**Parameters**

- `records : list[dict[str, int]]`
  List of membership records. Each record should be a dictionary with these fields:
  - 'parent_class_id': int - ID of the parent class
  - 'parent_object_id': int - ID of the parent object
  - 'collection_id': int - ID of the collection
  - 'child_class_id': int - ID of the child class
  - 'child_object_id': int - ID of the child object
- `chunksize : int, optional`
  Number of records to process in each batch, by default 10_000.
  Useful for controlling memory usage with large datasets.

**Returns**

- `bool`
  True if the operation was successful

**Raises**

- `KeyError`
  If any records are missing required fields

**See Also**

- `add_membership` : Add a single membership between two objects
- `create_membership_record` : Helper to create membership record dictionaries

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> # Create parent and children objects
>>> parent_id = db.add_object(ClassEnum.Region, "Region1")
>>> child_ids = []
>>> for i in range(5):
...     child_ids.append(db.add_object(ClassEnum.Node, f"Node{i}"))
>>> # Prepare membership records
>>> parent_class_id = db.get_class_id(ClassEnum.Region)
>>> child_class_id = db.get_class_id(ClassEnum.Node)
>>> collection_id = db.get_collection_id(
...     CollectionEnum.RegionNodes,
...     parent_class_enum=ClassEnum.Region,
...     child_class_enum=ClassEnum.Node,
... )
>>> # Create records
>>> records = []
>>> for child_id in child_ids:
...     records.append(
...         {
...             "parent_class_id": parent_class_id,
...             "parent_object_id": parent_id,
...             "collection_id": collection_id,
...             "child_class_id": child_class_id,
...             "child_object_id": child_id,
...         }
...     )
>>> # Bulk insert all memberships at once
>>> db.add_memberships_from_records(records)
True
```

### add_metadata

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L697)

```text
add_metadata(self, entity_type: Literal['object', 'membership', 'data'], entity_id: int, class_name: str, property_name: str, value: str, /, *, state: int | None=None) -> None
```

Add metadata to an entity (object, membership, or data).

### add_object

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L711)

```text
add_object(self, class_enum: ClassEnum, /, name: str, *, description: str | None=None, category: str | None=None, collection_enum: CollectionEnum | Literal[False] | None=None) -> int
```

Add an object to the database and append a system membership.

Creates a new object in the database with the given name and class. Automatically
creates a system membership for the object.

**Parameters**

- `name : str`
  Name of the object to be added
- `class_enum : ClassEnum`
  Class enumeration of the object, e.g., ClassEnum.Generator for a generator object
- `category : str, optional`
  Category of the object, by default "-"
- `description : str | None, optional`
  Description of the object, by default None
- `collection_enum : CollectionEnum | None | Literal[False] = None, optional`
  Collection for the system membership. If None, a default collection is determined
  based on the class, by default None

**Returns**

- `int`
  ID of the created object

**Raises**

- `sqlite.IntegrityError`
  If an object is inserted without a unique name/class pair

**See Also**

- `check_category_exists` : Check if a category exists for a specific class
- `add_category` : Add a new category for a given class
- `get_default_collection` : Get the default collection for a class
- `add_membership` : Add a membership between two objects

**Notes**

All objects need to have a system membership. If you want to add additional
membership(s) to other object(s), consider `add_membership` or `add_memberships`.

The database enforces uniqueness on the combination of name and class_id.

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> object_id = db.add_object("TestGenerator", ClassEnum.Generator)
1
```

### add_objects

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L798)

```text
add_objects(self, class_enum: ClassEnum, *object_names: str, category: str | None=None) -> None
```

Add multiple objects of the same class to the database in bulk.

This method efficiently adds multiple objects to the database in a single operation,
which is much more performant than calling add_object() multiple times. It also
creates system memberships for all objects in bulk.

**Parameters**

- `object_names : Iterable[str]`
  Names of the objects to be added
- `class_enum : ClassEnum`
  Class enumeration of the objects
- `category : str | None, optional`
  Category of the objects, by default None (which uses "-" as default category)

**Returns**

- `None`

**See Also**

- `add_object` : Add a single object
- `add_memberships_from_records` : Add multiple memberships in bulk
- `normalize_names` : Normalize object names for consistency
- `get_default_collection` : Get the default collection for a class

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> # Add multiple generators at once
>>> generator_names = ["Gen1", "Gen2", "Gen3", "Gen4", "Gen5"]
>>> db.add_objects(generator_names, class_enum=ClassEnum.Generator, category="Thermal")
```

### add_properties_from_records

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L871)

```text
add_properties_from_records(self, records: list[dict[str, Any]], /, *, object_class: ClassEnum, parent_class: ClassEnum=ClassEnum.System, collection: CollectionEnum, scenario: str, chunksize: int=10000) -> None
```

Bulk insert multiple properties from a list of records, with optional text data.

Efficiently adds multiple properties to multiple objects in batches using
transactions, which is significantly faster than calling add_property repeatedly.

Each record should contain an 'name' field and property-value pairs.
If records contain 'datafile_text' or 'timeslice' fields, that data will be
automatically attached to the property data records.

All properties are automatically marked as dynamic and enabled in the database.

**Parameters**

- `records : list[dict]`
  List of records where each record is a dictionary with:
  - 'name': str - Name of the object
  - property1: value1, property2: value2, ... - Property name-value pairs
  - 'datafile_text': str (optional) - File path text for DataFile
  - 'timeslice': str (optional) - Timeslice name
- `object_class : ClassEnum`
  Class enumeration of the objects (e.g., ClassEnum.Generator)
- `parent_class : ClassEnum, optional`
  Parent class enumeration, by default ClassEnum.System
- `collection : CollectionEnum`
  Collection enumeration for the properties (e.g., CollectionEnum.Generators)
- `scenario : str`
  Scenario name to associate with all properties
- `chunksize : int, optional`
  Number of records to process in each batch to control memory usage,
  by default 10_000

**Returns**

- `None`

**Raises**

- `ValueError`
  If records are improperly formatted or missing required fields
- `KeyError`
  If an object name doesn't exist in the database

**See Also**

- `add_property` : Add a single property
- `check_property_exists` : Check if properties exist for a collection
- `add_memberships_from_records` : Bulk insert multiple memberships
- `prepare_sql_data_params` : Utility for preparing SQL parameters from records

**Notes**

This method uses SQLite transactions to ensure all insertions are atomic.
If an error occurs during processing, the entire transaction is rolled back.

Properties are inserted directly using SQL for optimal performance, and all
added properties are automatically marked as dynamic and enabled.

The method automatically detects and processes 'datafile_text' and 'timeslice'
fields if present in the records.

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> # Create objects first
>>> db.add_object(ClassEnum.Generator, "Generator1")
>>> db.add_object(ClassEnum.Generator, "Generator2")
>>> # Prepare property records with optional datafile_text field
>>> records = [
...     {"name": "Generator1", "Max Capacity": 100.0, "datafile_text": "/path_to_file/gen1.txt"},
...     {"name": "Generator2", "Max Capacity": 150.0, "datafile_text": "/path_to_file/gen2.txt"},
... ]
>>> # Add properties in bulk - datafile_text is automatically detected and attached
>>> db.add_properties_from_records(
...     records,
...     object_class=ClassEnum.Generator,
...     collection=CollectionEnum.Generators,
...     scenario="Base Case",
... )
```

### add_attributes_from_records

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1021)

```text
add_attributes_from_records(self, records: list[dict[str, Any]], /, *, object_class: ClassEnum, chunksize: int=10000) -> None
```

Bulk insert attribute values for objects.

Efficiently adds multiple object-level attribute values in batches.
This method is much more efficient than calling `add_attribute` repeatedly.

Each record should contain:
    - 'name': object name
    - 'attribute': attribute name
    - 'value': attribute value

Alternatively, records may be provided in the following format:
    - {'name': ..., 'Attr1': val1, 'Attr2': val2}

Optional:
    - 'state'

**Parameters**

- `records : list[dict[str, Any]]`
  List of attribute records in explicit or wide format.
- `object_class : ClassEnum`
  Class of the objects.
- `chunksize : int, optional`
  Batch size for inserts, by default 10_000.

**Returns**

- `None`

**See Also**

- `add_attribute`
- `add_properties_from_records`
- `add_memberships_from_records`

**Examples**

```python
>>> records = [
...     {"name": "2020", "Step Type": 4.0, "Chrono Step Count": 366.0},
... ]
```

```python
>>> db.add_attributes_from_records(records, object_class=ClassEnum.Horizon)
```

### add_property

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1235)

```text
add_property(self, object_class_enum: ClassEnum, /, object_name: str, name: str, value: str | int | float, *, scenario: str | None=None, band: int | None=None, date_from: datetime | None=None, date_to: datetime | None=None, datafile_text: str | None=None, timeslice: str | None=None, collection_enum: CollectionEnum | None=None, parent_class_enum: ClassEnum | None=None, parent_object_name: str | None=None) -> int
```

Add a property for a given object in the database.

Adds a property with the specified value to an object, optionally associating
it with a scenario, band, date range, datafile text, and timeslice data.

**Parameters**

- `object_class_enum : ClassEnum`
  Class enumeration of the object
- `object_name : str`
  Name of the object to add the property to
- `name : str`
  Name of the property to add
- `value : str | int | float`
  Value to assign to the property
- `scenario : str | None, optional`
  Name of the scenario to associate with this property, by default None
- `band : str | int | None, optional`
  Band to associate with this property, by default None
- `date_from : datetime | None, optional`
  Start date for this property, by default None
- `date_to : datetime | None, optional`
  End date for this property, by default None
- `datafile_text : str | None, optional`
  File path text to associate with this property (for DataFile objects), by default None
- `timeslice : str | None, optional`
  Timeslice name to associate with this property, by default None
- `collection_enum : CollectionEnum | None, optional`
  Collection enumeration for the property. If None, a default is determined
  based on the object class, by default None
- `parent_class_enum : ClassEnum | None, optional`
  Class enumeration of the parent object. If None, defaults to ClassEnum.System,
  by default None
- `parent_object_name : str | None, optional`
  Name of the parent object. If None, membership is resolved from
  `parent_class_enum`, `collection_enum`, and `object_name`.

**Returns**

- `int`
  ID of the created property data record

**Raises**

- `NameError`
  If the property name does not exist for the specified collection
  If the object name does not exist

**See Also**

- `get_object_id` : Get the ID for an object
- `get_default_collection` : Get the default collection for a class
- `list_valid_properties` : List valid property names for a collection
- `get_property_id` : Get the ID for a property
- `get_membership_id` : Get the ID for a membership
- `check_scenario_exists` : Check if a scenario exists
- `add_object` : Add a new object to the database

**Notes**

The method validates that the property name is valid for the given collection.
If a scenario is provided but doesn't exist, it will be created automatically.
The datafile_text parameter stores file path metadata for DataFile objects.
The timeslice parameter stores timeslice name metadata.

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Generator, "Generator1")
>>> db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", 100.0)
1
```

### add_scenario

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1360)

```text
add_scenario(self, name: str, category: str | None=None) -> int
```

Add a scenario object in the database.

**Parameters**

- `name: str`
  Name of the scenario
- `category: str | None`
  Name of the category for the scenario

**See Also**

- `get_scenario_id` : Get the ID for a scenario
- `list_scenarios` : List all available scenarios in the database

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_scenario("TestScenario")
>>> db.list_scenarios()
[("TestScenario")]
```

### add_report

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1392)

```text
add_report(self, /, *, object_name: str, property: str, collection: CollectionEnum, parent_class: ClassEnum, child_class: ClassEnum, phase_id: int=4, report_period: bool | None=None, report_summary: bool | None=True, report_statistics: bool | None=None, report_samples: bool | None=None, write_flat_files: bool=False) -> None
```

Add an output property configuration to an existing report.

Adds a property and its output options to the specified ``Report`` object.
The report object must already exist; call `add_object` first only when
creating a new report object. Reports define what data will be available for
post-processing after simulation runs.

**Parameters**

- `object_name : str`
  Name of the existing report object to add the configuration to
- `property : str`
  Name of the property to report on
- `collection : CollectionEnum`
  Collection enumeration that contains the property
- `parent_class : ClassEnum`
  Parent class enumeration for the collection
- `child_class : ClassEnum`
  Child class enumeration for the collection
- `phase_id : int, optional`
  Phase ID for the report (1=LT Plan, 2=PASA, 3=MT Schedule, 4=ST Schedule),
  by default 4 (ST Schedule)
- `report_period : bool | None, optional`
  Whether to report period data, by default None
- `report_summary : bool | None, optional`
  Whether to report summary data, by default True
- `report_statistics : bool | None, optional`
  Whether to report statistics, by default None
- `report_samples : bool | None, optional`
  Whether to report samples, by default None
- `write_flat_files : bool, optional`
  Whether to output flat files, by default False

**Raises**

- `NameError`
  If the specified property does not exist for the collection

**See Also**

- `get_object_id` : Get the ID for an object
- `get_collection_id` : Get the ID for a collection
- `list_valid_properties_report` : List valid report properties for a collection

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Report, "GeneratorOutput")
>>> db.add_report(
...     object_name="GeneratorOutput",
...     property="Generation",
...     collection=CollectionEnum.Generators,
...     parent_class=ClassEnum.System,
...     child_class=ClassEnum.Generator,
...     report_period=True,
...     report_summary=True,
... )
```

### add_text

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1508)

```text
add_text(self, text_class: ClassEnum, text_value: str | int | float, data_id: int) -> int
```

Add text data to a property data record.

**Parameters**

- `text_class : ClassEnum`
  Name of the Text class to be added
- `text_value : str`
  Value of the text to be added
- `data_id : int`
  Data to be tagged with the Text object

**Raises**

- `AssertionError`
  If the class does not exist

**Returns**

- `bool`
  True if the query was succesfull

### add_time_slice

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1539)

```text
add_time_slice(self, name: str, /, *, interval: str, start_datetime: str, end_datetime: str, description: str | None=None) -> int
```

Add a time slice definition to the database.

### add_variable_tag

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1552)

```text
add_variable_tag(self, data_id: int, variable_name: str, /, *, value: str | float | None=None) -> int
```

Add a Variable tag to a property data record.

### backup_database

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1563)

```text
backup_database(self, target_path: str | Path) -> None
```

Backup the in-memory database to a file.

### copy_object

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1567)

```text
copy_object(self, object_class: ClassEnum, original_object_name: str, new_object_name: str, copy_properties: bool=True, copy_attributes: bool=True) -> int
```

Copy an object and its memberships, attributes, properties, tags and texts.

### copy_object_memberships

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1612)

```text
copy_object_memberships(self, object_class: ClassEnum, original_name: str, new_name: str) -> dict[int, int]
```

Copy all existing memberships of old object to the new object.

### create_object_scenario

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1779)

```text
create_object_scenario(self, object_name: str, scenario_name: str, properties: dict[str, Any], /, *, object_class: ClassEnum, description: str | None=None, collection: CollectionEnum | None=None, parent_class: ClassEnum | None=None, base_scenario: str | None=None) -> int
```

Create a new scenario with specific property values for an object.

### create_schema

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1902)

```text
create_schema(self, schema: str | None=None, *, seed_defaults: bool=False, version: int | str | tuple[int, ...] | None=None) -> bool
```

Create database schema from SQL script.

Initializes the database schema by executing SQL statements, either from
the default schema or from a provided schema string. Optionally, this can
preload a versioned master template into the new schema.

**Parameters**

- `schema : str | None, optional`
  Direct SQL schema content to execute. If None, uses the default schema,
  by default None
- `seed_defaults : bool, optional`
  If True, seed minimal classes/collections/System object after schema
  creation so workflows like ``add_object`` work immediately on a fresh
  database without loading XML. Mutually exclusive with ``version``;
  passing both raises ``ValueError``, by default False
- `version : int | str | tuple[int, ...] | None, optional`
  PLEXOS major version used to preload the matching master template
  from ``plexosdb/config``. Supported versions are 9, 10, 11, and 12.
  All forms are equivalent: ``9``, ``"9.2"``, ``"v9.2R6"``, and
  ``(9, 2, 6)`` all load the v9 master template.
  If None, no master template is loaded.

**Returns**

- `bool`
  True if initialization succeeded, False if it failed

**See Also**

- `_db.executescript` : Execute a SQL script in the database
- `PLEXOS_DEFAULT_SCHEMA` : Default schema SQL content

**Notes**

This is typically the first method called after initializing a new PlexosDB
instance, as it sets up the required tables for the database.

Calling this method with defaults creates schema structure only; it does
not seed lookup/model rows needed by higher-level object workflows.
Use ``seed_defaults=True`` (or load XML / provide seeded custom schema)
when you want methods like ``add_object`` to work immediately.

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
True
```

```python
>>> db = PlexosDB()
>>> db.create_schema(seed_defaults=True)
True
```

```python
>>> db = PlexosDB()
>>> db.create_schema(version="11.0")
True
```

```python
>>> custom_schema = '''
... CREATE TABLE IF NOT EXISTS t_config (
...     element TEXT PRIMARY KEY,
...     value TEXT
... );
... '''
>>> db = PlexosDB()
>>> db.create_schema(schema=custom_schema)
True
```

### delete_attribute

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L1999)

```text
delete_attribute(self, attribute_name: str, /, *, object_name: str, object_class: ClassEnum) -> None
```

Delete an attribute value from an object.

Removes an object-level attribute value from the database.

**Parameters**

- `attribute_name : str`
  Name of the attribute to delete.
- `object_name : str`
  Name of the object the attribute belongs to.
- `object_class : ClassEnum`
  Class enumeration of the object.

**Returns**

- `None`

**Raises**

- `NotFoundError`
  If the object does not exist, the attribute is not defined for the
  object's class or the attribute value is not assigned to the object.

**Examples**

```python
>>> db.delete_attribute(
...     "Enabled",
...     object_name="Base_Model",
...     object_class=ClassEnum.Model,
... )
```

### delete_category

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2064)

```text
delete_category(self, category: str, /, *, class_name: ClassEnum) -> None
```

Delete a category from the database.

### delete_membership

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2068)

```text
delete_membership(self, parent_object_name: str, child_object_name: str, /, *, parent_class: ClassEnum, child_class: ClassEnum, collection: CollectionEnum) -> None
```

Delete a membership between two objects.

### delete_metadata

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2081)

```text
delete_metadata(self, entity_type: Literal['object', 'membership', 'data'], entity_id: int, class_name: str, property_name: str) -> None
```

Delete metadata from an entity.

### delete_object

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2091)

```text
delete_object(self, class_enum: ClassEnum, /, *, name: str) -> None
```

Delete an object and its memberships from the database.

Default behaviour is to remove all the references of the object including memberships and data.

### delete_property

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2104)

```text
delete_property(self, object_class: ClassEnum, object_name: str, /, *, property_name: str, collection: CollectionEnum | None=None, parent_class: ClassEnum | None=None, parent_object_name: str | None=None, scenario: str | None=None) -> None
```

Delete a property from an object.

Removes a specific property from an object, including all associated data
such as tags (scenarios), text data, and date ranges. If a scenario is
specified, only the property data associated with that scenario is deleted.

**Parameters**

- `object_class : ClassEnum`
  Class enumeration of the object
- `object_name : str`
  Name of the object containing the property
- `property_name : str`
  Name of the property to delete
- `collection : CollectionEnum | None, optional`
  Collection enumeration for the property. If None, uses the default
  collection for the object class, by default None
- `parent_class : ClassEnum | None, optional`
  Parent class enumeration for the property. If None, defaults to
  ClassEnum.System, by default None
- `parent_object_name : str | None, optional`
  Parent object name. If None, membership is resolved by parent class,
  child class, collection, and child object name.
- `scenario : str | None, optional`
  Name of the scenario to filter by. If specified, only deletes
  property data associated with this scenario, by default None

**Raises**

- `NotFoundError`
  If the object does not exist
  If the property does not exist for the object
  If the specified scenario does not exist

**See Also**

- `delete_object` : Delete an entire object and its properties
- `add_property` : Add a property to an object
- `get_object_properties` : Get properties for an object

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Generator, "Generator1")
>>> db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", 100.0)
>>> db.delete_property(ClassEnum.Generator, "Generator1", property_name="Max Capacity")
```

### delete_text

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2222)

```text
delete_text(self, data_id: int, /, *, class_id: int) -> None
```

Delete text data from a property data record.

### get_attribute

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2232)

```text
get_attribute(self, object_class: ClassEnum, /, *, object_name: str, attribute_name: str) -> Any
```

Get an assigned attribute value for a specific object.

### get_attribute_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2257)

```text
get_attribute_id(self, class_enum: ClassEnum, /, name: str) -> int
```

Return the ID for a given attribute.

Retrieves the unique identifier for an attribute with the specified name and class.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration the category belongs to
- `name : str`
  Name of the attribute

**Returns**

- `int`
  ID of the attribute

**Raises**

- `NotFoundError`
  If the attribute does not exist for the specified class.

### get_attributes

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2296)

```text
get_attributes(self, object_name: str, /, *, object_class: ClassEnum, attribute_names: str | Iterable[str] | None=None) -> list[dict[str, Any]]
```

Retrieve assigned attribute values for a specific object.

**Parameters**

- `object_name : str`
  Name of the object.
- `object_class : ClassEnum`
  Class of the object.
- `attribute_names : str | Iterable[str] | None, optional`
  Attribute name or names to retrieve. If omitted, retrieves all
  assigned attribute values.

**Returns**

- `list[dict[str, Any]]`
  Attribute-value records with ``name``, ``attribute``, ``value``,
  and ``state`` keys. Returns an empty list when the object has no
  assigned attribute values.

**Raises**

- `NotFoundError`
  If the object does not exist for the requested class.

### get_category_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2364)

```text
get_category_id(self, class_enum: ClassEnum, /, name: str) -> int
```

Return the ID for a given category.

Retrieves the unique identifier for a category with the specified name and class.

**Parameters**

- `category : str`
  Name of the category
- `class_enum : ClassEnum`
  Class enumeration the category belongs to

**Returns**

- `int`
  ID of the category

**Raises**

- `AssertionError`
  If the category does not exist

**See Also**

- `check_category_exists` : Check if a category exists
- `add_category` : Add a new category

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_category(ClassEnum.Generator, "my_category")
>>> db.get_category_id(ClasEnum.Generator, "my_category")
1
```

### get_category_max_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2416)

```text
get_category_max_id(self, class_enum: ClassEnum) -> int
```

Return the current maximum rank for a given category class.

Determines the highest rank value currently assigned to any category
of the specified class, useful for adding new categories with unique ranks.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration to check

**Returns**

- `int`
  Maximum rank value for the class's categories

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `add_category` : Add a new category

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_category("Category1", ClassEnum.Generator)
>>> db.get_category_max_id(ClassEnum.Generator)
1
```

### get_class_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2464)

```text
get_class_id(self, class_enum: ClassEnum) -> int
```

Return the ID for a given class.

Retrieves the unique identifier for the specified class enumeration.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration to get the ID for

**Returns**

- `int`
  ID of the class

**Raises**

- `AssertionError`
  If the class does not exist

**See Also**

- `ClassEnum` : Enumeration of available classes

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.get_class_id(ClassEnum.Generator)
15  # Example ID
```

### get_collection_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2500)

```text
get_collection_id(self, collection: CollectionEnum, /, parent_class_enum: ClassEnum, child_class_enum: ClassEnum) -> int
```

Return the ID for a given collection.

Retrieves the unique identifier for a collection based on its name and associated
parent and child classes.

**Parameters**

- `collection : CollectionEnum`
  Collection enumeration to get the ID for
- `parent_class_enum : ClassEnum`
  Parent class enumeration for the collection
- `child_class_enum : ClassEnum`
  Child class enumeration for the collection

**Returns**

- `int`
  ID of the collection

**Raises**

- `AssertionError`
  If the collection does not exist with the specified parent and child classes

**See Also**

- `CollectionEnum` : Enumeration of available collections
- `get_class_id` : Get the ID for a class

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.get_collection_id(CollectionEnum.Generators, ClassEnum.System, ClassEnum.Generator)
25  # Example ID
```

### get_config

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2558)

```text
get_config(self, element: str | None=None) -> dict[str, Any] | list[dict[str, Any]]
```

Get configuration values from the database.

**Parameters**

- `element : str | None, optional`
  Configuration element to retrieve. If omitted, return all
  configuration entries.

**Returns**

- `dict[str, Any] | list[dict[str, Any]]`
  A single configuration record when ``element`` is provided, or
  all configuration records ordered by element.

**Raises**

- `NotFoundError`
  If the requested element does not exist.

**Examples**

Retrieve a single configuration entry by its element name:

```python
>>> db.get_config("Culture")
{'element': 'Culture', 'value': 'en-AU English (Australia)'}
```

Retrieve all entries, ordered by element, and inspect one:

```python
>>> configurations = db.get_config()
>>> configurations[0]
{'element': 'Culture', 'value': 'en-AU English (Australia)'}
```

### get_custom_columns

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2602)

```text
get_custom_columns(self, class_enum: ClassEnum | None=None) -> list[dict[str, Any]]
```

Get custom columns, optionally filtered by class.

**Parameters**

- `class_enum : ClassEnum | None, optional`
  Class to filter by. If omitted, return custom columns for all
  classes, including columns without an assigned class.

**Returns**

- `list[dict[str, Any]]`
  Custom-column records with their database fields and the related
  class name, when available.

**Examples**

For a database containing a custom column assigned to ``Generator``:

```python
>>> custom_columns = db.get_custom_columns()
>>> custom_columns[0]["name"]
'__get_custom_columns_test__'
>>> generator_columns = db.get_custom_columns(ClassEnum.Generator)
>>> generator_columns[0]["class_name"]
'Generator'
```

### get_membership_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2648)

```text
get_membership_id(self, /, parent_name: str, child_name: str, collection: CollectionEnum) -> int
```

Return the ID for a given membership.

Retrieves the unique identifier for a membership between parent and child objects
in the specified collection.

**Parameters**

- `parent_name : str`
  Name of the parent object
- `child_name : str`
  Name of the child object
- `collection : CollectionEnum`
  Collection enumeration defining the relationship type

**Returns**

- `int`
  ID of the membership

**Raises**

- `AssertionError`
  If the membership does not exist

**See Also**

- `add_membership` : Add a new membership between objects

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.System, "System")
>>> db.add_object(ClassEnum.Generator, "Generator1")
>>> db.add_membership(
...     "System", "Generator1", ClassEnum.System, ClassEnum.Generator, CollectionEnum.Generators
... )
>>> db.get_membership_id("System", "Generator1", CollectionEnum.Generators)
1
```

### list_object_memberships

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2711)

```text
list_object_memberships(self, class_enum: ClassEnum, /, name: str, category: str | None=None, collection: CollectionEnum | None=None, exclude_system_membership: bool=False) -> list[dict[str, Any]]
```

Retrieve all memberships for a given object.

By default it returns the system membership.

**Parameters**

- `class_enum : ClassEnum`
  Class of the object
- `name : str`
  Name of the object to get its memberships.
- `collection : CollectionEnum | None, optional`
  Collection to filter memberships.
- `exclude_system_membership : bool, optional`
  If True, exclude system memberships.

**Returns**

- `list[dict]`
  A list of dicts representing memberships. Each tuple is structured as:
  (parent_class_id, child_class_id, parent_object_name, child_object_name, collection_id,
  return self.query(query_string=query_string, params=params)
  parent_class_name, collection_name).

**Raises**

- `KeyError`
  If any of the object_names do not exist.

### get_memberships_system

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2792)

```text
get_memberships_system(self, *object_names: Iterable[str] | str, object_class: ClassEnum, collection: CollectionEnum | None=None) -> list[dict[str, Any]]
```

Retrieve memberships for the requested object names.

**Parameters**

- `object_names : str or list[str]`
  Name or list of names of the objects to get their memberships.
  You can pass multiple string arguments or a single list of strings.
- `object_class : ClassEnum`
  Class of the objects.
- `collection : CollectionEnum | None, optional`
  Collection used to filter memberships. When provided, results are
  limited to memberships under the System parent class for that
  collection.

**Returns**

- `list[dict[str, Any]]`
  Membership rows for the requested object names in ``object_class``.
  Names that do not exist are ignored.

### get_metadata

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2861)

```text
get_metadata(self, entity_type: Literal['object', 'membership', 'data'], entity_id: int, /, *, class_name: str | None=None, property_name: str | None=None) -> list[dict[str, Any]]
```

Retrieve metadata for an entity, optionally filtered by class and property.

**Parameters**

- `entity_type : Literal["object", "membership", "data"]`
  Type of entity whose metadata to retrieve.
- `entity_id : int`
  Identifier of the object, membership, or data record.
- `class_name : str | None, optional`
  Metadata class to filter by.
- `property_name : str | None, optional`
  Metadata property to filter by.

**Returns**

- `list[dict[str, Any]]`
  Matching metadata records with the entity ID, class, property,
  value, and state fields. Returns an empty list when no records match.

**Raises**

- `ValueError`
  If ``entity_type`` is not ``"object"``, ``"membership"``, or ``"data"``.

**Examples**

Retrieve all metadata for an object, or narrow it by class and property:

```python
>>> metadata = db.get_metadata("object", object_id)
>>> matching_metadata = db.get_metadata(
...     "object", object_id, class_name="PLEXOS", property_name="Source"
... )
```

### get_object_data_ids

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L2931)

```text
get_object_data_ids(self, class_enum: ClassEnum, /, name: str, property_names: str | Iterable[str] | None=None, *, parent_class_enum: ClassEnum=ClassEnum.System, collection_enum: CollectionEnum | None=None, category: str | None=None) -> list[int]
```

Get all the data_id values for a given object in the database.

Retrieves all data IDs that match the specified criteria for an object,
optionally filtered by property names, parent class, collection, and category.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration of the object
- `name : str`
  Name of the object to retrieve data IDs for
- `property_names : str | Iterable[str] | None, optional`
  Names of specific properties to filter by, by default None
- `parent_class_enum : ClassEnum, optional`
  Parent class enumeration, by default ClassEnum.System
- `collection_enum : CollectionEnum | None, optional`
  Collection enumeration to filter by, by default None
  (if not specified, the default collection for the class is used)
- `category : str | None, optional`
  Category to filter by, by default None

**Returns**

- `list[int]`
  List of data_id values that match the criteria

**Raises**

- `KeyError`
  If the specified category does not exist
- `NameError`
  If any specified property does not exist for the collection

**See Also**

- `check_property_exists` : Check if properties exist for a collection
- `check_category_exists` : Check if a category exists
- `list_valid_properties` : List valid property names for a collection

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Generator, "Generator1")
>>> db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", 100.0)
>>> db.get_object_data_ids(ClassEnum.Generator, "Generator1")
[1]
```

### get_object_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3037)

```text
get_object_properties(self, class_enum: ClassEnum, /, name: str, property_names: str | Iterable[str] | None=None, *, parent_class_enum: ClassEnum | None=None, collection_enum: CollectionEnum | None=None, category: str | None=None, scenario: str | Iterable[str] | None=None, scenario_category: str | Iterable[str] | None=None) -> list[PropertyRecord]
```

Retrieve properties for a specific object.

Gets all properties for the specified object, optionally filtered by
property names, collection, and category.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration of the object
- `name : str`
  Name of the object to retrieve properties for
- `property_names : str | Iterable[str] | None, optional`
  Names of specific properties to retrieve. If None, gets all properties, by default None
- `parent_class_enum : ClassEnum | None, optional`
  Parent class enumeration for filtering properties, by default None
  (defaults to ClassEnum.System if not specified)
- `collection_enum : CollectionEnum | None, optional`
  Collection enumeration to filter properties by, by default None
  (if not specified, the default collection for the class is used)
- `category : str | None, optional`
  Category to filter by, by default None
- `scenario : str | Iterable[str] | None, optional`
  Scenario name(s) to filter properties by, by default None
- `scenario_category : str | Iterable[str] | None, optional`
  Scenario category name(s) to filter properties by, by default None

**Returns**

- `list[PropertyRecord]`
  List of dictionaries containing property information.
  See PropertyRecord TypedDict for full field definitions including:
  name, property, value, unit, category, scenario_name, etc.

**Raises**

- `NoPropertiesError`
  If the specified object does not have any properties
- `NameError`
  If the specified property does not exist for the collection
- `KeyError`
  If the specified category does not exist

**See Also**

- `iterate_properties` : Iterate through properties with efficient memory handling
- `check_property_exists` : Check if properties exist for a collection
- `list_valid_properties` : List valid property names for a collection
- `has_properties` : Check if an object has any properties

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Generator, "Generator1")
>>> db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", 100.0)
>>> properties = db.get_object_properties(ClassEnum.Generator, "Generator1")
>>> properties[0]["property"]
'Max Capacity'
>>> properties[0]["value"]
100.0
```

### get_object_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3133)

```text
get_object_id(self, class_enum: ClassEnum, /, name: str, *, category: str | None=None) -> int
```

Return the ID for a given object.

Retrieves the unique identifier for an object with the specified name and class,
optionally filtering by category.

**Parameters**

- `object_name : str`
  Name of the object
- `class_enum : ClassEnum`
  Class enumeration of the object
- `category : str | None, optional`
  Category name to filter by, by default None

**Returns**

- `int`
  ID of the object

**Raises**

- `AssertionError`
  If the object does not exist
- `KeyError`
  If no object matches the criteria

**See Also**

- `check_object_exists` : Check if an object exists
- `add_object` : Add a new object to the database
- `get_category_id` : Get the ID for a category

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Generator, "Generator1" category="Thermal")
>>> db.get_object_id("Generator1", ClassEnum.Generator)
1
```

### get_objects_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3198)

```text
get_objects_id(self, *object_names: Iterable[str] | str, class_enum: ClassEnum) -> list[int]
```

Get object_ids for a list of names for a given class.

### get_plexos_version

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3220)

```text
get_plexos_version(self) -> tuple[int, ...] | None
```

Return the version information of the PLEXOS model.

### get_property_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3224)

```text
get_property_id(self, property_name: str, /, *, collection_enum: CollectionEnum, child_class_enum: ClassEnum, parent_class_enum: ClassEnum | None=None) -> int
```

Return the ID for a given property.

Retrieves the unique identifier for a property based on its name and associated
collection and classes.

**Parameters**

- `property_name : str`
  Name of the property
- `collection_enum : CollectionEnum`
  Collection enumeration the property belongs to
- `child_class_enum : ClassEnum`
  Child class enumeration for the property
- `parent_class_enum : ClassEnum | None, optional`
  Parent class enumeration for the property, by default None

**Returns**

- `int`
  ID of the property

**Raises**

- `AssertionError`
  If the property does not exist

**See Also**

- `get_collection_id` : Get the ID for a collection
- `list_valid_properties` : List valid property names for a collection

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.get_property_id(
...     "Max Capacity",
...     collection_enum=CollectionEnum.Generators,
...     child_class_enum=ClassEnum.Generator,
...     parent_class_enum=ClassEnum.System,
... )
42  # Example ID
```

### get_property_unit

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3286)

```text
get_property_unit(self, property_name: str, /, collection_enum: CollectionEnum, parent_class_enum: ClassEnum, child_class_enum: ClassEnum) -> str
```

Get the unit for a specific property.

Returns an empty string when the property has no unit value.

**Examples**

```python
>>> db.get_property_unit(
...     "Max Capacity",
...     collection_enum=CollectionEnum.Generators,
...     parent_class_enum=ClassEnum.System,
...     child_class_enum=ClassEnum.Generator,
... )
'MW'
```

### get_scenario_id

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3326)

```text
get_scenario_id(self, name: str) -> int
```

Return the ID for a given scenario.

Retrieves the object id for a scenario based on its name.

**Parameters**

- `name : str`
  Name of the scenario

**Returns**

- `int`
  ID of the property

**Raises**

- `AssertionError`
  If the property does not exist

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_scenario("TestScenario")
42  # Example ID
>>> db.get_scenario_id("TestScenario")
42
```

### get_text

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3358)

```text
get_text(self, data_id: int, /, *, class_id: int | None=None) -> list[dict[str, Any]]
```

Retrieve text data associated with a property data record.

**Parameters**

- `data_id : int`
  Property data record identifier.
- `class_id : int | None, optional`
  Limit results to a text class.

**Returns**

- `list[dict[str, Any]]`
  Matching text records ordered by class ID.

**Examples**

```python
>>> text_row = db.query("SELECT data_id, class_id FROM t_text ORDER BY data_id, class_id LIMIT 1")
>>> data_id, class_id = text_row[0]
>>> db.get_text(data_id, class_id=class_id))
[{'data_id': 1600, 'class_id': 76, 'value': 'M4-10', 'state': None, 'action_id': None}]
```

### get_unit

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3395)

```text
get_unit(self, unit_id: int) -> dict[str, Any]
```

Get details for a specific unit.

**Raises**

- `NotFoundError`
  If the unit does not exist.

**Examples**

```python
>>> unit_row = db.query("SELECT unit_id FROM t_unit ORDER BY unit_id LIMIT 1")
>>> unit_id = unit_row[0][0]
>>> from pprint import pprint
>>> pprint(db.get_unit(unit_id))
{'default': '-',
 'description': None,
 'imperial_energy': None,
 'imperial_level': None,
 'imperial_volume': None,
 ...
 'unit_id': 0,
 'value': '-'}
```

### has_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3423)

```text
has_properties(self, class_enum: ClassEnum, /, name: str, *, collection_enum: CollectionEnum | None=None, category: str | None=None) -> bool
```

Check if the given object has any properties associated with it.

Determines whether an object has any properties in the database that match
the specified criteria, optionally filtered by collection and category.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration of the object
- `name : str`
  Name of the object to check
- `collection_enum : CollectionEnum | None, optional`
  Collection enumeration to filter by, by default None
  (if not specified, the default collection for the class is used)
- `category : str | None, optional`
  Category to filter by, by default None

**Returns**

- `bool`
  True if the object has at least one property matching the criteria,
  False otherwise

**Raises**

- `KeyError`
  If the specified category does not exist

**See Also**

- `get_object_properties` : Get properties for an object
- `check_category_exists` : Check if a category exists
- `get_default_collection` : Get the default collection for a class

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Generator, "Generator1")
>>> db.has_properties(ClassEnum.Generator, "Generator1")
False
>>> db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", 100.0)
>>> db.has_properties(ClassEnum.Generator, "Generator1")
True
```

### import_from_csv

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3500)

```text
import_from_csv(self, source_path: str | Path, /, *, tables: list[str] | None=None) -> None
```

Import data from CSV files into the database.

### iterate_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3504)

```text
iterate_properties(self, /, *, class_enum: ClassEnum | None=None, object_names: str | Iterable[str] | None=None, property_names: str | Iterable[str] | None=None, parent_class: ClassEnum | None=None, collection: CollectionEnum | None=None, category: str | None=None, scenario: str | Iterable[str] | None=None, scenario_category: str | Iterable[str] | None=None, batch_size: int=1000) -> Iterator[PropertyRecord]
```

Iterate through properties with chunked processing to handle large datasets efficiently.

This method efficiently retrieves properties for multiple objects of the specified class,
processing data in chunks to minimize memory usage. Results are yielded one at a time
as dictionaries.

**Parameters**

- `class_enum : ClassEnum | None, optional`
  Class enumeration of the objects to retrieve properties for
- `object_names : str | Iterable[str] | None, optional`
  Names of specific objects to retrieve properties for. If None, gets properties
  for all objects of the specified class
- `property_names : str | Iterable[str] | None, optional`
  Names of specific properties to retrieve. If None, gets all properties
- `parent_class : ClassEnum | None, optional`
  Parent class enumeration for filtering properties, defaults to ClassEnum.System
- `collection : CollectionEnum | None, optional`
  Collection enumeration to filter properties by
- `category : str | None, optional`
  Category name to filter objects by
- `scenario : str | Iterable[str] | None, optional`
  Scenario name(s) to filter property rows by
- `scenario_category : str | Iterable[str] | None, optional`
  Scenario category name(s) to filter property rows by
- `batch_size : int, optional`
  Number of records to process in each database query chunk, by default 1000

**Yields**

- `PropertyRecord`
  Dictionary containing property information with keys such as:
  name, property, value, unit, category, scenario_name, etc.
  See PropertyRecord TypedDict for full field definitions.

**Raises**

- `NameError`
  If a specified property does not exist for the collection
- `NotFoundError`
  If specified objects or category do not exist
- `KeyError`
  If specified category does not exist

### list_attributes

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3629)

```text
list_attributes(self, class_enum: ClassEnum) -> list[str]
```

Get all attributes for a specific class.

Retrieves the names of attributes associated with the specified class.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration to list attributes

**Returns**

- `list[str]`
  List of attributes names

**Raises**

- `AssertionError`
  If the query fails

### list_categories

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3663)

```text
list_categories(self, class_enum: ClassEnum) -> list[str]
```

Get all categories for a specific class.

Retrieves the names of all categories associated with the specified class.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration to list categories for

**Returns**

- `list[str]`
  List of category names

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `add_category` : Add a new category
- `check_category_exists` : Check if a category exists

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_category("Thermal", ClassEnum.Generator)
>>> db.add_category("Renewable", ClassEnum.Generator)
>>> db.list_categories(ClassEnum.Generator)
['Thermal', 'Renewable']
```

### list_child_objects

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3711)

```text
list_child_objects(self, object_name: str, /, *, parent_class: ClassEnum, child_class: ClassEnum | None=None, collection: CollectionEnum | None=None) -> list[dict[str, Any]]
```

List all child objects for a given parent object.

Retrieves all child objects that have a membership relationship with the specified
parent object, optionally filtered by child class and collection.

**Parameters**

- `object_name : str`
  Name of the parent object
- `parent_class : ClassEnum`
  Class enumeration of the parent object
- `child_class : ClassEnum | None, optional`
  Class enumeration to filter child objects by, by default None
- `collection : CollectionEnum | None, optional`
  Collection enumeration to filter relationships by, by default None

**Returns**

- `list[dict]`
  List of dictionaries containing child object information with keys:
  - object_id: ID of the child object
  - name: Name of the child object
  - class_name: Class name of the child object
  - collection_name: Name of the collection/relationship type
  - membership_id: ID of the membership relationship

**Raises**

- `AssertionError`
  If the parent object does not exist

**See Also**

- `list_parent_objects` : List parent objects for a given child object
- `get_object_id` : Get the ID for an object
- `get_class_id` : Get the ID for a class
- `get_collection_id` : Get the ID for a collection
- `add_membership` : Add a membership between two objects

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Region, "Region1")
>>> db.add_object(ClassEnum.Node, "Node1")
>>> db.add_object(ClassEnum.Node, "Node2")
>>> db.add_membership(
...     parent_class_enum=ClassEnum.Region,
...     child_class_enum=ClassEnum.Node,
...     parent_object_name="Region1",
...     child_object_name="Node1",
...     collection_enum=CollectionEnum.ReferenceNode,
... )
>>> db.add_membership(
...     parent_class_enum=ClassEnum.Region,
...     child_class_enum=ClassEnum.Node,
...     parent_object_name="Region1",
...     child_object_name="Node2",
...     collection_enum=CollectionEnum.ReferenceNode,
... )
>>> children = db.list_child_objects(
...     "Region1",
...     parent_class=ClassEnum.Region,
...     child_class=ClassEnum.Node
...     collection=CollectionEnum.ReferenceNode
... )
>>> len(children)
2
>>> children[0]["name"]
'Node1'
>>> children[0]["class_name"]
'Node'
```

### list_classes

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3828)

```text
list_classes(self) -> list[str]
```

Return all classes names in the database.

**Returns**

- `list[str]`
  List of valid classes names

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `query` : Query the SQL database

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.list_classes()
["System", "Generator", ...]
```

### list_collections

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3857)

```text
list_collections(self, /, *, parent_class: ClassEnum | None=None, child_class: ClassEnum | None=None) -> list[dict[str, Any]]
```

List all available collections in the database.

**Parameters**

- `parent_class : ClassEnum | None, optional`
  Filter by parent class, by default None
- `child_class : ClassEnum | None, optional`
  Filter by child class, by default None

**Returns**

- `list[dict]`
  List of collections with their details including id, name,
  parent_class, child_class, description, etc.

### list_objects_by_class

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3906)

```text
list_objects_by_class(self, class_enum: ClassEnum, /, *, category: str | None=None) -> list[str]
```

Return all objects of a specific class.

Retrieves names of all objects belonging to the specified class,
optionally filtered by category.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration to filter oRaises
- `category : str | None, optional`
  Category name to filter by, by default None

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `get_class_id` : Get the ID for a class
- `add_object` : Add an object to the database
- `query` : Query the SQL database bjects by

**Returns**

- `list[dict]`
  List of object names

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `get_class_id` : Get the ID for a class
- `add_object` : Add an object to the database
- `query` : Query the SQL database

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object("Generator1", ClassEnum.Generator)
>>> db.add_object("Generator2", ClassEnum.Generator)
>>> db.list_objects_by_class(ClassEnum.Generator)
['Generator1', 'Generator2']
```

### list_parent_objects

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L3981)

```text
list_parent_objects(self, object_name: str, /, *, child_class: ClassEnum, parent_class: ClassEnum | None=None, collection: CollectionEnum | None=None) -> list[dict[str, Any]]
```

List all parent objects for a given child object.

Retrieves all parent objects that have a membership relationship with the specified
child object, optionally filtered by parent class and collection.

**Parameters**

- `object_name : str`
  Name of the child object
- `child_class : ClassEnum`
  Class enumeration of the child object
- `parent_class : ClassEnum | None, optional`
  Class enumeration to filter parent objects by, by default None
- `collection : CollectionEnum | None, optional`
  Collection enumeration to filter relationships by, by default None

**Returns**

- `list[dict]`
  List of dictionaries containing parent object information with keys:
  - object_id: ID of the parent object
  - name: Name of the parent object
  - class_name: Class name of the parent object
  - collection_name: Name of the collection/relationship type
  - membership_id: ID of the membership relationship

**Raises**

- `AssertionError`
  If the child object does not exist

**See Also**

- `list_child_objects` : List child objects for a given parent object
- `get_object_id` : Get the ID for an object
- `get_class_id` : Get the ID for a class
- `get_collection_id` : Get the ID for a collection
- `add_membership` : Add a membership between two objects

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Region, "Region1")
>>> db.add_object(ClassEnum.Region, "Region2")
>>> db.add_object(ClassEnum.Node, "Node1")
>>> db.add_membership(
...     parent_class_enum=ClassEnum.Region,
...     child_class_enum=ClassEnum.Node,
...     parent_object_name="Region1",
...     child_object_name="Node1",
...     collection_enum=CollectionEnum.ReferenceNode,
... )
>>> db.add_membership(
...     parent_class_enum=ClassEnum.Region,
...     child_class_enum=ClassEnum.Node,
...     parent_object_name="Region2",
...     child_object_name="Node1",
...     collection_enum=CollectionEnum.ReferenceNode,
... )
>>> parents = db.list_parent_objects(
...     "Node1",
...     child_class=ClassEnum.Node,
...     parent_class=ClassEnum.Region,
...     collection=CollectionEnum.ReferenceNode,
... )
>>> parents[0]["name"]
'Region1'
```

### list_reports

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4095)

```text
list_reports(self) -> list[dict[str, Any]]
```

List all defined reports in the database.

### list_scenarios

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4099)

```text
list_scenarios(self) -> list[str]
```

Return all scenarios in the database.

**Returns**

- `list[str]`
  List of valid scenario names

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `query` : Query the SQL database

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Generator, "Generator1")
>>> db.add_property(
...     ClassEnum.Generator,
...     "Generator1",
...     "Max Capacity",
...     100.0,
...     scenario="Scenario",
... )
>>> db.list_scenarios()
["Scenario"]
```

### list_models

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4143)

```text
list_models(self) -> list[str]
```

Return all models in the database.

**Returns**

- `list[str]`
  List of valid models names

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `query` : Query the SQL database

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Model, "model_01")
>>> db.list_models()
["model_01"]
```

### list_scenarios_by_model

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4180)

```text
list_scenarios_by_model(self, model_name: str) -> list[str]
```

List all scenarios associated with a given model.

**Parameters**

- `model_name : str`
  Name of the model to list scenarios for.

**Returns**

- `list[str]`
  List of scenario names associated with the model. Returns an empty list if none found.

**Examples**

```python
>>> db.add_object(ClassEnum.Model, "Model1")
>>> db.add_object(ClassEnum.Scenario, "Scenario1")
>>> db.add_membership(
...     parent_class_enum=ClassEnum.Model,
...     child_class_enum=ClassEnum.Scenario,
...     parent_object_name="Model1",
...     child_object_name="Scenario1",
...     collection_enum=CollectionEnum.Scenarios,
... )
>>> db.list_scenarios_by_model("Model1")
['Scenario1']
```

### list_units

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4220)

```text
list_units(self) -> list[dict[int, str]]
```

List all available units in the database.

### list_valid_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4227)

```text
list_valid_properties(self, collection_enum: CollectionEnum, /, parent_class_enum: ClassEnum, child_class_enum: ClassEnum) -> list[str]
```

Return list of valid property names for a collection.

Retrieves all valid property names that can be used with a specific collection,
optionally filtered by parent and child classes.

**Parameters**

- `collection_enum : CollectionEnum`
  Collection enumeration to list properties for
- `parent_class_enum : ClassEnum | None, optional`
  Parent class enumeration to filter by, by default None
- `child_class_enum : ClassEnum | None, optional`
  Child class enumeration to filter by, by default None

**Returns**

- `list[str]`
  List of valid property names

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `get_collection_id` : Get the ID for a collection
- `check_property_exists` : Check if properties exist for a collection

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.list_valid_properties(
...     CollectionEnum.Generators,
...     parent_class_enum=ClassEnum.System,
...     child_class_enum=ClassEnum.Generator,
... )
['Max Capacity', 'Min Stable Level', 'Heat Rate']  # Example properties
```

### list_valid_properties_report

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4282)

```text
list_valid_properties_report(self, collection_enum: CollectionEnum, /, parent_class_enum: ClassEnum, child_class_enum: ClassEnum) -> list[str]
```

Return list of valid property names for reports.

Retrieves all valid property names that can be used with a specific collection filtered by parent and
child classes.

**Parameters**

- `collection_enum : CollectionEnum`
  Collection enumeration to list properties for
- `parent_class_enum : ClassEnum | None, optional`
  Parent class enumeration to filter by, by default None
- `child_class_enum : ClassEnum | None, optional`
  Child class enumeration to filter by, by default None

**Returns**

- `list[str]`
  List of valid property report names

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `get_collection_id` : Get the ID for a collection

### query

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4325)

```text
query(self, query_string: str, params: tuple[Any, ...] | dict[str, Any] | None=None) -> list[Any]
```

Execute a read-only query and return all results.

Executes a SQL SELECT query against the database and returns the results.

**Parameters**

- `query_string : str`
  SQL query to execute (SELECT statements only)
- `params : tuple[Any, ...] | dict[str, Any] | None, optional`
  Parameters to bind to the query, by default None

**Returns**

- `list`
  Query results (tuples or named tuples based on initialization)

**Raises**

- `sqlite3.Error`
  If a database error occurs

**See Also**

- `_db.query` : Underlying database query method

**Notes**

This method should ONLY be used for SELECT statements. For INSERT/UPDATE/DELETE,
use execute() instead.

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object("Generator1", ClassEnum.Generator)
>>> db.query("SELECT name FROM t_object WHERE class_id = ?", (15,))  # 15 = Generator class_id
[('Generator1',)]
```

### set_config

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4366)

```text
set_config(self, element: str, value: str) -> None
```

Set a configuration value in the database.

### set_date_range

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4370)

```text
set_date_range(self, data_id: int, /, *, date_from: str | None=None, date_to: str | None=None) -> None
```

Set the date range for a property data record.

### to_csv

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4381)

```text
to_csv(self, target_path: str | Path, /, *, tables: list[str] | None=None) -> None
```

Export selected tables or the entire database to CSV files.

### to_xml

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4385)

```text
to_xml(self, target_path: str | Path) -> bool
```

Convert SQLite to XML format.

This method takes all the tables of the SQLite database and creates the
appropriate tags based on the column name, exporting the complete database
as a PLEXOS-compatible XML file.

**Parameters**

- `target_path: str | Path`
  Path to serialize the database

**Returns**

- `bool`
  True if the creation succeeded, False if it failed

**See Also**

- `from_xml` : Create a database from XML file
- `XMLHandler` : Class that handles XML parsing and generation

**Notes**

The exported XML file follows the PLEXOS MasterDataSet format and can be
imported directly into PLEXOS.

**Examples**

```python
>>> # Initialize a database with some data
>>> db = PlexosDB()
>>> db.create_schema()
>>> # Add some objects and properties
>>> db.add_object(ClassEnum.Generator, "Generator1", description="Example generator")
>>> db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", 100.0)
>>> # Add another object with a scenario
>>> db.add_object(ClassEnum.Generator, "Generator2")
>>> db.add_property(ClassEnum.Generator, "Generator2", "Max Capacity", 200.0, scenario="High Demand")
>>> # Export the database to XML
>>> xml_path = Path("output_model.xml")
>>> result = db.to_xml(xml_path)
>>> result
True
>>> xml_path.exists()
True
>>> # Create a new database from the generated XML
>>> new_db = PlexosDB.from_xml(xml_path)
>>> generators = new_db.list_objects_by_class(ClassEnum.Generator)
>>> sorted(generators)
['Generator1', 'Generator2']
```

### update_attribute

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4461)

```text
update_attribute(self, attribute_name: str, new_value: str | float | int, /, *, object_name: str, object_class: ClassEnum) -> None
```

Update an attribute value for an object.

### update_category

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4473)

```text
update_category(self, category: str, new_name: str, /, *, class_name: ClassEnum) -> None
```

Update a category name.

### update_object

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4477)

```text
update_object(self, class_enum: ClassEnum, object_name: str, *, new_name: str, new_category: str | None=None, new_description: str | None=None) -> bool
```

Update an object's attributes.

**Parameters**

- `class_enum : ClassEnum`
  Class enumeration of the object
- `object_name : str`
  Current name of the object to update
- `new_name : str`
  New name for the object
- `new_category : str | None, optional`
  New category for the object, by default None
- `new_description : str | None, optional`
  New description for the object, by default None

**Returns**

- `bool`
  True if the update was successful

**Raises**

- `AssertionError`
  If the query fails

**See Also**

- `get_object_id` : Get the ID for an object
- `get_category_id` : Get the ID for a category
- `add_object` : Add a new object to the database

**Examples**

```python
>>> db = PlexosDB()
>>> db.create_schema()
>>> db.add_object(ClassEnum.Generator, "ThermalGen1", category="Thermal")
>>> db.add_object(ClassEnum.Generator, "SolarGen1", category="Solar")
>>> # Update just the name
>>> db.update_object(ClassEnum.Generator, "ThermalGen1", new_name="SolarGen")
True
>>> # Update name, category, and description
>>> db.update_object(
...     ClassEnum.Generator,
...     "SolarGen",
...     new_name="SolarGen2",
...     new_category="Solar",
...     new_description="Updated from thermal to solar generator",
... )
True
```

### update_properties

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4557)

```text
update_properties(self, updates: list[dict[str, Any]]) -> None
```

Update multiple matching property data records in one transaction.

Each update mapping uses the selectors accepted by `update_property`.
Unlike `update_property`, a bulk selector may match multiple data
records; every matching record is updated. In particular, omitting
``band`` updates all bands for the selected object, property, scenario,
and membership. Include ``band`` when only one band should be changed.

### update_property

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L4863)

```text
update_property(self, object_name: str, property_name: str, new_value: str | None, /, *, object_class: ClassEnum, scenario: str | None=None, band: str | int | None=None, collection: CollectionEnum | None=None, parent_class: ClassEnum | None=None, parent_object_name: str | None=None) -> None
```

Update exactly one existing property data record.

**Parameters**

- `object_name : str`
  Name of the object whose property is updated.
- `property_name : str`
  Name of the property to update.
- `new_value : str | None`
  New value to store in the property data record.
- `object_class : ClassEnum`
  Class of the object.
- `scenario : str | None, optional`
  Scenario used to select the property data record. If omitted, only
  an unscoped property record is considered.
- `band : str | int | None, optional`
  Band number used to select the property data record. Strings and
  integers are accepted. If omitted, the selector must match exactly
  one data record or ``ValueError`` is raised.
- `collection : CollectionEnum | None, optional`
  Property collection. Defaults to the collection for ``object_class``.
- `parent_class : ClassEnum | None, optional`
  Parent class for the membership. Defaults to ``ClassEnum.System``.
- `parent_object_name : str | None, optional`
  Explicit parent object used to disambiguate memberships.

**Raises**

- `NotFoundError`
  If the object, membership, or selected property data record does not exist.
- `NameError`
  If ``property_name`` is invalid for the selected collection and classes.
- `ValueError`
  If more than one property data record matches the selectors or if
  ``band`` is not an integer.

**Notes**

The update changes only ``t_data.value``. Existing scenario tags, bands,
dates, and text metadata are preserved.

### update_scenario

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L5013)

```text
update_scenario(self, scenario_name: str, /, *, new_name: str | None=None, new_category: str | None=None, new_description: str | None=None) -> None
```

Update a scenario's properties.

### update_text

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L5025)

```text
update_text(self, data_id: int, text_value: str, /, *, class_id: int) -> None
```

Update text data for a property data record.

### validate_value_by_rule

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L5037)

```text
validate_value_by_rule(value: SQLiteValue, validation_rule: str) -> ValidationResult
```

Validate a numeric value against a PLEXOS validation rule.

Supports inclusive ``Between X And Y``, ``In (X,Y,Z)``, and comparisons
``>=X``, ``<=X``, ``<X``, and ``>X``. Surrounding whitespace is ignored.
Empty rules accept any value. Non-numeric values, malformed rules, and
unsupported rules return an invalid ``ValidationResult`` with an error
message; valid results have an empty error message.

**Examples**

```python
>>> PlexosDB.validate_value_by_rule(50.0, "Between 1 And 100").is_valid
True
>>> PlexosDB.validate_value_by_rule(150.0, "Between 1 And 100").error_message
'Value 150.0 must be between 1.0 and 100.0'
```

### validate_database

[Source](https://github.com/NatLabRockies/plexosdb/blob/36b632a1a0dd1fd24258b2fad2ec11ebd7e6a207/src/plexosdb/db.py#L5055)

```text
validate_database(self, /, *, fix_issues: bool=False) -> bool
```

Validate the packaged PLEXOS schema and database relationships.

Checks that required tables and columns exist, SQLite integrity and
foreign keys are valid, classes are consistent across objects,
memberships, attributes, and properties, and integer-valued attributes
marked with ``is_integer``. By default, validation does not modify the
database. Findings are ``DatabaseValidationFinding`` instances with a
``DatabaseValidationCategory`` and a message.

**Parameters**

- `fix_issues : bool, optional`
  If True, repair membership class IDs only when the referenced object
  and collection agree, and only when membership findings are the sole
  findings. Repairs are retained only if validation then passes.
  Otherwise, only the repairs are rolled back and findings are raised.
  An existing caller transaction remains open and is not committed or
  rolled back; without one, successful repairs are committed.

**Returns**

- `bool`
  True when the database passes all supported checks.

**Raises**

- `DatabaseValidationError`
  If one or more checks fail. The exception's ``findings`` attribute
  contains typed validation findings.
- `TypeError`
  If ``fix_issues`` is not a bool.
