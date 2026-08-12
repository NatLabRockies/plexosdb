# Adding Properties to Objects

Properties define attributes of objects in your PLEXOS model, such as a
generator's capacity or a node's location.

## Basic Property Addition

```python
from plexosdb import PlexosDB
from plexosdb.enums import ClassEnum, CollectionEnum

# Initialize database
db = PlexosDB()
db.create_schema()

# Create a generator object if it doesn't exist
if not db.check_object_exists(ClassEnum.Generator, "Generator1"):
    db.add_object(ClassEnum.Generator, "Generator1")

# Add a property to the generator
db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Max Capacity",
    value=100.0
)

# Add another property
db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Min Stable Level",
    value=20.0
)
```

## Adding Properties with Scenarios

Properties can be associated with specific scenarios:

```python
# Add a property with a scenario
db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Max Capacity",
    value=120.0,
    scenario="High Demand"
)
```

## Adding Properties with Bands

For properties that have band data:

```python
# Add a property with a band
db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Heat Rate",
    value=10.5,
    band=1
)
```

## Adding Text Data to Properties

Properties can include additional text information:

```python
from plexosdb.enums import ClassEnum

# Add a property with text data
db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Max Capacity",  # Use a valid property name
    value="Main unit",
    text={ClassEnum.Generator: "Primary generation unit"}
)
```

## Updating Properties

Use `update_property` to change the value of an existing property without
removing its scenario, band, date, or text metadata:

```python
db.update_property(
    "Generator1",
    "Max Capacity",
    125.0,
    object_class=ClassEnum.Generator,
)
```

When a property has multiple bands, pass `band` to update only the matching
band. Pass `scenario` to update a scenario-specific value. If `scenario` is
omitted, only the base, non-scenario property is updated.

```python
db.update_property(
    "Generator1",
    "Heat Rate",
    9.8,
    object_class=ClassEnum.Generator,
    band=2,
    scenario="High Demand",
)
```

The `collection` and `parent_class` arguments can be supplied when the property
belongs to a non-default collection or membership:

```python
db.update_property(
    "Generator1",
    "Max Capacity",
    130.0,
    object_class=ClassEnum.Generator,
    collection=CollectionEnum.Generators,
    parent_class=ClassEnum.System,
)
```

The method raises `NotFoundError` when the object or matching property row does
not exist, and `NameError` when the property is invalid for the selected
collection.

## Bulk Adding Properties

For efficiency when adding many properties at once (use the flat format; the
nested format is accepted but deprecated and will emit a warning):

```python
# Flat format (recommended)
flat_records = [
    {"name": "Generator1", "property": "Max Capacity", "value": 100, "band": 1},
    {"name": "Generator1", "property": "Max Capacity", "value": 200, "band": 2},
    {"name": "Generator2", "property": "Heat Rate", "value": 9.9, "datafile_text": "gen2.csv"},
]

# Nested format (legacy; will be removed in the future)
nested_records = [
    {"name": "Generator3", "properties": {"Max Capacity": {"value": 150, "band": 1}}},
]

db.add_properties_from_records(
    flat_records + nested_records,
    object_class=ClassEnum.Generator,
    parent_class=ClassEnum.System,
    collection=CollectionEnum.Generators,
    scenario="Base Case",
)
```

## Checking Valid Properties

Before adding properties, you can check if they are valid for a collection:

```python
# Check if properties are valid
valid_props = db.list_valid_properties(
    CollectionEnum.Generators,
    parent_class_enum=ClassEnum.System,
    child_class_enum=ClassEnum.Generator
)
print(f"Valid generator properties: {valid_props}")
```

```{warning}
Adding an invalid property will raise a NameError. Always check if properties are valid for your collection.
```
