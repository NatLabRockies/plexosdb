# Adding Properties to Objects

Properties define attributes of objects in your PLEXOS model, such as a
generator's capacity or a node's location.

The examples in this guide use the PlexosDB 1.6.1 API. The first argument to
`add_property` is positional-only; the remaining property arguments are passed
by name where that makes the example easier to read.

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

## Adding DataFile and Timeslice Text

Use `datafile_text` to attach file-path metadata to a property. This is the
supported replacement for the older `text` example; `add_property` does not
accept a `text` keyword. Use `timeslice` for timeslice metadata.

```python
# Attach DataFile metadata to the property data record.
db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Max Capacity",
    value=100.0,
    datafile_text="gen1.csv",
)

# Attach timeslice metadata when the property is timeslice-specific.
db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Max Capacity",
    value=110.0,
    timeslice="Peak",
)
```

`datafile_text` and `timeslice` store text metadata on the property data record;
they do not change the property's numeric or string `value`. A DataFile or
Timeslice object does not need to be created manually for these associations.

## Adding Date- and Scenario-Specific Properties

Scenarios are created automatically when the supplied scenario does not yet
exist. Date bounds must be `datetime` objects.

```python
from datetime import datetime

db.add_property(
    ClassEnum.Generator,
    "Generator1",
    "Max Capacity",
    120.0,
    scenario="High Demand",
    date_from=datetime(2030, 1, 1),
    date_to=datetime(2030, 12, 31),
    band=1,
)
```

For non-default memberships, pass `collection_enum`, `parent_class_enum`, and
optionally `parent_object_name` to select the membership to which the property
is added. When omitted, the default collection is selected, the parent class
defaults to `ClassEnum.System`, and the membership is resolved from the object
and collection.

## Bulk Adding Properties

For efficiency when adding many properties at once, use flat records. Each flat
record contains `name`, `property`, and `value`; `band`, `datafile_text`, and
`timeslice` are optional per-record fields. The legacy nested format is still
accepted but deprecated and emits a warning.

```python
# Flat format (recommended)
flat_records = [
    {"name": "Generator1", "property": "Max Capacity", "value": 100, "band": 1},
    {"name": "Generator1", "property": "Max Capacity", "value": 200, "band": 2},
    {
        "name": "Generator2",
        "property": "Heat Rate",
        "value": 9.9,
        "datafile_text": "gen2.csv",
        "timeslice": "Peak",
    },
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

The bulk method applies the supplied `scenario` to all records, defaults
`parent_class` to `ClassEnum.System`, and processes records in chunks of 10,000
by default. Set `chunksize` to tune memory use for larger imports. It uses a
transaction, so an insertion error rolls back the bulk operation.

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
Adding an invalid property raises `NameError`; a missing object raises
`NotFoundError`. Always check if properties are valid for your collection and
create the target object before adding its properties.
```
