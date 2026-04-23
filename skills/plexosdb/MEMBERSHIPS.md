# plexosdb Memberships Reference

Use this document when wiring parent/child relationships through PLEXOS
collections.

## Why memberships matter

Most PLEXOS object data is only meaningful **within a collection**.
A generator's `Max Capacity` property exists on the `Generators`
collection of `System`; a generator's fuel is expressed through the
`Fuels` collection that links `Generator` to `Fuel`. Without the right
membership row, many properties cannot be attached and many downstream
queries return empty.

## Core concepts

- **Class** (`ClassEnum`): the type of thing (`Generator`, `Node`,
  `Region`, `System`, `Fuel`, etc.).
- **Collection** (`CollectionEnum`): a typed relationship with a
  parent class and a child class. Examples:
  - `Generators` with parent `System`, child `Generator`.
  - `Fuels` with parent `Generator`, child `Fuel`.
  - `Nodes` with parent `Generator`, child `Node` (head node).
- **Membership**: a row wiring a specific `(parent_object,
  collection, child_object)` triple. Properties and attributes are
  attached *to a membership*, not directly to an object in isolation.

## Core APIs

- `db.add_membership(parent_class_enum, parent_object_name,
  child_class_enum, child_object_name, collection_enum) -> int`,
  creates a membership row and returns its id.
- `db.add_memberships_from_records(records)`, bulk path for many
  memberships (record dicts carrying all five keys above).
- `db.get_membership_id(...)`, resolves the membership row id.
- `db.check_membership_exists(...)`, existence probe.
- `db.list_object_memberships(class_enum, name, *, collection=None,
  parent=None)`, inspects memberships attached to a given object.
- `db.get_memberships_system(class_enum, name)`, convenience for the
  System-parent memberships of an object.
- `db.list_parent_objects(class_enum, name, collection_enum=...)`,
  navigates "who points at me?".
- `db.list_child_objects(class_enum, name, collection_enum=...)`,
  navigates "who do I point at?".
- `db.delete_membership(...)`, removes a single membership.
- `db.copy_object_memberships(class_enum, original_name, new_name)`,
  duplicates every membership row from one object to another.

## Mandatory field patterns

`add_membership(...)` requires all of:

- `parent_class_enum`
- `parent_object_name`
- `child_class_enum`
- `child_object_name`
- `collection_enum`

The collection must be valid for the `(parent_class, child_class)`
pair; invalid combinations raise at insert time.

## Recommended wiring path

1. Create the parent object (often `System` already exists after
   `create_schema()`).
2. Create the child object with `add_object(...)`.
3. Attach the child to the parent via `add_membership(...)`.
4. Only then attach properties/attributes to the child.

```python
from plexosdb import PlexosDB, ClassEnum, CollectionEnum

db = PlexosDB()
db.create_schema()

# System root already exists after create_schema()

db.add_object(ClassEnum.Generator, "GEN01", category="Thermal")
db.add_membership(
    parent_class_enum=ClassEnum.System,
    parent_object_name="System",
    child_class_enum=ClassEnum.Generator,
    child_object_name="GEN01",
    collection_enum=CollectionEnum.Generators,
)

# Now properties on Generator via the System-owned Generators
# collection will attach correctly.
db.add_property(ClassEnum.Generator, "GEN01", "Max Capacity", 100.0)
```

## Cross-class wiring example

```python
# Wire a node to a region through the regions collection on Node
db.add_membership(
    parent_class_enum=ClassEnum.Node,
    parent_object_name="NODE_A",
    child_class_enum=ClassEnum.Region,
    child_object_name="REGION_WEST",
    collection_enum=CollectionEnum.Region,
)

# Wire a generator to its head node
db.add_membership(
    parent_class_enum=ClassEnum.Generator,
    parent_object_name="GEN01",
    child_class_enum=ClassEnum.Node,
    child_object_name="NODE_A",
    collection_enum=CollectionEnum.Nodes,
)
```

## Bulk membership insert

For large models, prefer the bulk path:

```python
records = [
    {
        "parent_class_enum": ClassEnum.System,
        "parent_object_name": "System",
        "child_class_enum": ClassEnum.Generator,
        "child_object_name": name,
        "collection_enum": CollectionEnum.Generators,
    }
    for name in generator_names
]
db.add_memberships_from_records(records)
```

Advantages:

- Single SQLite transaction, much faster than per-row inserts.
- Fails fast with row-index context on the first invalid record.

## Copy pattern

```python
# Duplicate an object and preserve its relationship graph
db.copy_object(
    ClassEnum.Generator,
    original_name="GEN01",
    new_name="GEN02",
    copy_properties=False,
)
db.copy_object_memberships(
    ClassEnum.Generator,
    original_name="GEN01",
    new_name="GEN02",
)
```

Use this when you need a structurally identical sibling but want to
diverge properties after the clone.

## Query behavior

- `list_object_memberships(...)` returns per-row dicts describing the
  collection, parent object, and child object — useful for diffing
  what an object participates in.
- `list_parent_objects(...)` and `list_child_objects(...)` are the
  two-way traversal primitives; prefer them over hand-written SQL.
- Use `collection_enum` filters in both to narrow the traversal to a
  single relationship type.

## Common mistakes

- Attaching a property **before** the enabling membership exists, then
  wondering why the property is invisible to PLEXOS.
- Copying an object with `copy_object(...)` but forgetting to call
  `copy_object_memberships(...)` (unless `copy_memberships=True` is
  set on the copy call).
- Using raw strings for class/collection names instead of `ClassEnum`
  and `CollectionEnum` — silently creates ambiguous or duplicate rows.
- Deleting an object without removing its memberships (use
  `delete_object(...)` which handles cascade correctly, or
  `delete_membership(...)` explicitly before bulk reshaping).

## Related references

- [REFERENCE.md](./REFERENCE.md) for the base PlexosDB API surface.
- [PROPERTIES.md](./PROPERTIES.md) for what to attach *after* the
  membership is in place.
- [SCENARIOS.md](./SCENARIOS.md) for scenario-tagged overrides.
