# Copying Objects

PlexosDB allows you to create copies of existing objects along with their properties, memberships, and related property records.

## Basic Object Copying

Copy an object and all its properties:

```python
from plexosdb import PlexosDB
from plexosdb.enums import ClassEnum, CollectionEnum

# Initialize database
db = PlexosDB.from_xml("/path/to/model.xml")

# Assumes the model already contains a generator named "Generator1".

db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Max Capacity",
    value=100.0,
    scenario="Base Case"
)

db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Max Energy",
    value=20.0,
    scenario="Base Case"
)

# Copy a generator with all its properties
new_object_id = db.copy_object(
    object_class=ClassEnum.Generator,
    original_object_name="Generator1",
    new_object_name="Generator1_Copy",
    copy_properties=True  # Default is True
)

print(f"Created new object with ID: {new_object_id}")
```

## Copying Objects Without Properties

You can also copy the object and its memberships without copying properties:

```python
# Add Generator object
db.add_object(ClassEnum.Generator, "Generator1")

# Add property
db.add_property(
    ClassEnum.Generator,
    object_name="Generator1",
    name="Max Capacity",
    value=20.0,
    scenario="Base Case"
)

# Copy object structure only
new_object_id = db.copy_object(
    object_class=ClassEnum.Generator,
    original_object_name="Generator1",
    new_object_name="Generator1_Skeleton",
    copy_properties=False
)
```

## Copying Memberships

When copying an object, PlexosDB also attempts to copy its memberships (except any that cannot be recreated due to model constraints):

```python
# First create some objects with memberships
db.add_object(ClassEnum.Region, "Region1")
db.add_object(ClassEnum.Node, "Node1")

# Add membership
db.add_membership(
    parent_class_enum=ClassEnum.Region,
    child_class_enum=ClassEnum.Node,
    parent_object_name="Region1",
    child_object_name="Node1",
    collection_enum=CollectionEnum.ReferenceNode
)

# Now copy the node with its memberships
new_object_id = db.copy_object(
    object_class=ClassEnum.Node,
    original_object_name="Node1",
    new_object_name="Node1_Copy",
    copy_properties=False
)

# Check the memberships of the new object
memberships = db.list_object_memberships(
    ClassEnum.Node,
    name="Node1_Copy"
)
print(f"New object has {len(memberships)} memberships")
```

## Programmatic Membership Copying

You can also copy all non-system memberships programmatically:

```python
db.add_object(ClassEnum.Node, "Node1")
db.add_object(ClassEnum.Generator, "Generator1")
db.add_object(ClassEnum.Generator, "Generator1_Copy")

db.add_membership(
    parent_class_enum=ClassEnum.Generator,
    child_class_enum=ClassEnum.Node,
    parent_object_name="Generator1",
    child_object_name="Node1",
    collection_enum=CollectionEnum.Nodes
)

membership_mapping = db.copy_object_memberships(
    object_class=ClassEnum.Generator,
    original_name="Generator1",
    new_name="Generator1_Copy"
)

print(f"Copied {len(membership_mapping)} memberships")
```

## Practical Example: Duplicating a Set of Objects

This example shows how to duplicate a group of related objects:

```python
# Create a function to copy memberships from an existing generator
def duplicate_generator_with_connections(db, original_name, new_name):
    # Create the new generator (memberships are copied manually below)
    db.add_object(ClassEnum.Generator, new_name)

    # Find and copy all connections
    memberships = db.list_object_memberships(
        ClassEnum.Generator,
        name=original_name,
        exclude_system_membership=True
    )

    # Process each membership to maintain the network structure
    for membership in memberships:
        if membership["parent_name"] == original_name:
            # Original generator was the parent, connect child to new generator
            db.add_membership(
                parent_class_enum=ClassEnum[membership["parent_class_name"]],
                child_class_enum=ClassEnum[membership["child_class_name"]],
                parent_object_name=new_name,
                child_object_name=membership["child_name"],
                collection_enum=CollectionEnum[membership["collection_name"]]
            )
        else:
            # Original generator was the child, connect new generator to parent
            db.add_membership(
                parent_class_enum=ClassEnum[membership["parent_class_name"]],
                child_class_enum=ClassEnum[membership["child_class_name"]],
                parent_object_name=membership["parent_name"],
                child_object_name=new_name,
                collection_enum=CollectionEnum[membership["collection_name"]]
            )

    return new_name

# Existing generator to duplicate
db.add_object(ClassEnum.Generator, "Generator1")

# Use the function to duplicate a generator with all its connections
duplicate_generator_with_connections(db, "Generator1", "Generator1_Full_Copy")
```

```{note}
When copying objects with properties that reference other objects (like "Node" for a generator), you may need to update these properties manually if you want them to reference different objects.
```
