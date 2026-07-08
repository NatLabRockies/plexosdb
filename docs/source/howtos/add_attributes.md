# Working with Attributes

Objects in PlexosDB can have attributes stored in the `t_attribute_data` table.

Attributes are different from properties in the following ways:

- Attribute definitions are valid for a class and are stored in `t_attribute`.
- Attribute values are assigned directly to individual objects in
  `t_attribute_data`.

```{note}
See the [API Reference](../api/index.md) for class-specific attribute
tables that list available attributes, default values, validation rules and
descriptions.
```

## Listing available attributes per `ClassEnum`

We can use `list_attributes()` to see which attributes are valid for a specific
class. This returns definitions, not values assigned to a particular object.

```python
from plexosdb import ClassEnum, PlexosDB
db = PlexosDB.from_xml("/path/to/your/model.xml")

attributes = db.list_attributes(ClassEnum.Generator)
print(attributes)
```

## Adding an attribute to an existing object

We can use `add_attribute()` to assign one attribute value. The object must
already exist and the attribute name must be valid for its class.

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
db.add_attribute(
    ClassEnum.Generator,
    "Generator1",
    attribute_name="Latitude",
    attribute_value=100.0,
)
```

## Extracting a single attribute from an object

We can use `get_attribute()` when we know the attribute name and need its
assigned value.

```python
step_count = db.get_attribute(
    ClassEnum.Generator,
    object_name="Generator1",
    attribute_name="Latitude",
)
print(step_count)
```

## Extracting all assigned attributes from an object

We can use `get_attributes()` to retrieve all values assigned to an object.

```python
attributes = db.get_attributes(
    "2020",
    object_class=ClassEnum.Horizon,
)

for attribute in attributes:
    print(attribute["attribute"], attribute["value"])
```

The result contains dictionaries with the following keys:

```text
name
attribute
value
state
```

We can also filter to one attribute or a group of attributes.

```python
step_type = db.get_attributes(
    "2020",
    object_class=ClassEnum.Horizon,
    attribute_names="Step Type",
)

step_attributes = db.get_attributes(
    "2020",
    object_class=ClassEnum.Horizon,
    attribute_names=["Chrono Step Count", "Step Type"],
)
```

If the object exists but has no assigned values matching the request,
`get_attributes()` returns an empty list.

## Checking and deleting assigned attributes

We can use `check_attribute_exists()` to determine whether an object has an
assigned value for a particular attribute.

```python
has_step_count = db.check_attribute_exists(
    "Chrono Step Count",
    object_name="2020",
    object_class=ClassEnum.Horizon,
)

print(has_step_count)
```

We can use `delete_attribute()` to remove an assigned value.

```python
db.delete_attribute(
    "Chrono Step Count",
    object_name="2020",
    object_class=ClassEnum.Horizon,
)
```

## Adding attributes in bulk

We can use `add_attributes_from_records()` when assigning values to many
objects. The method accepts either explicit records or a wide format.

For explicit records we can use one row per object and attribute:

```python
db.add_attributes_from_records(
    [
        {"name": "2020", "attribute": "Chrono Step Count", "value": 366},
        {"name": "2020", "attribute": "Step Type", "value": 4},
        {"name": "2021", "attribute": "Chrono Step Count", "value": 365},
    ],
    object_class=ClassEnum.Horizon,
)
```

For wide records we can use one column per attribute:

```python
db.add_attributes_from_records(
    [
        {
            "name": "2020",
            "Chrono Step Count": 366,
            "Step Type": 4,
        },
        {
            "name": "2021",
            "Chrono Step Count": 365,
            "Step Type": 4,
        },
    ],
    object_class=ClassEnum.Horizon,
)
```
