# plexosdb Memberships Reference

Use this document when wiring parent/child relationships through PLEXOS
collections.

## Why memberships matter

Most PLEXOS object data is only meaningful **within a collection**. A
generator's `Max Capacity` property exists on the `Generators` collection of
`System`; a generator's fuel is expressed through the `Fuels` collection that
links `Generator` to `Fuel`. Without the right membership row, many properties
cannot be attached and many downstream queries return empty.

## Core concepts

- **Class** (`ClassEnum`): the type of thing (`Generator`, `Node`, `Region`,
  `System`, `Fuel`, etc.).
- **Collection** (`CollectionEnum`): a typed relationship with a parent class
  and a child class. Examples:
  - `Generators` with parent `System`, child `Generator`.
  - `Fuels` with parent `Generator`, child `Fuel`.
  - `Nodes` with parent `Generator`, child `Node` (head node).
- **Membership**: a row wiring a specific
  `(parent_object, collection, child_object)` triple. Properties and attributes
  are attached _to a membership_, not directly to an object in isolation.

## Core APIs

- `db.add_membership(parent_class_enum, parent_object_name, child_class_enum, child_object_name, collection_enum) -> int`,
  creates a membership row and returns its id.
- `db.add_memberships_from_records(records)`, bulk path for many memberships.
  Records use resolved integer IDs, not enums or names: `parent_class_id`,
  `parent_object_id`, `collection_id`, `child_class_id`, `child_object_id` (see
  "Bulk membership insert").
- `db.get_membership_id(...)`, resolves the membership row id.
- `db.check_membership_exists(parent_object_name, child_object_name, *, parent_class, child_class, collection) -> bool`,
  existence probe.
- `db.list_object_memberships(class_enum, name, *, category=None, collection=None, exclude_system_membership=False)`,
  inspects memberships attached to a given object.
- `db.get_memberships_system(*object_names, object_class, collection=None)`,
  convenience for the System-parent memberships of one or more objects.
- `db.list_parent_objects(class_enum, name, collection_enum=...)`, navigates
  "who points at me?".
- `db.list_child_objects(class_enum, name, collection_enum=...)`, navigates "who
  do I point at?".
- `db.delete_membership(...)`, remove a single membership. Not implemented in
  current plexosdb (raises `NotImplementedError`); use `delete_object(...)`,
  which cascades memberships, instead.
- `db.copy_object_memberships(class_enum, original_name, new_name)`, duplicates
  every membership row from one object to another.

## Mandatory field patterns

`add_membership(...)` requires all of:

- `parent_class_enum`
- `parent_object_name`
- `child_class_enum`
- `child_object_name`
- `collection_enum`

The collection must be valid for the `(parent_class, child_class)` pair; invalid
combinations raise at insert time.

## Recommended wiring path

1. Bootstrap: `PlexosDB.from_xml(path)`, or `PlexosDB()` +
   `create_schema(seed_defaults=True)` for a fresh model.
2. Create each object with `add_object(...)`. This automatically creates the
   object's `System` membership through its default collection, so there is no
   separate step to wire an object into `System`.
3. Add explicit `add_membership(...)` rows only for non-System (cross-class)
   relationships.
4. Attach properties/attributes after the object exists.

```python
from plexosdb import PlexosDB, ClassEnum

db = PlexosDB()
db.create_schema(seed_defaults=True)

# add_object also creates the System -> Generator membership via the
# Generators collection. Do NOT add that membership again; a duplicate
# raises AssertionError.
db.add_object(ClassEnum.Generator, "GEN01", category="Thermal")

# Named PLEXOS properties require the collection's property catalog,
# which is present when the model was loaded via from_xml(...).
db.add_property(ClassEnum.Generator, "GEN01", "Max Capacity", 100.0)
```

## Cross-class wiring example

Cross-class collections must exist in the property/collection catalog. A bare
`create_schema(seed_defaults=True)` seeds only System->child collections, so
load the model via `from_xml(...)` (or a full schema) before wiring these.

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

For large models, prefer the bulk path. Records use resolved integer IDs, not
enums or names:

```python
parent_class_id = db.get_class_id(ClassEnum.Generator)
child_class_id = db.get_class_id(ClassEnum.Node)
collection_id = db.get_collection_id(
    CollectionEnum.Nodes,
    parent_class_enum=ClassEnum.Generator,
    child_class_enum=ClassEnum.Node,
)
parent_id = db.get_object_id(ClassEnum.Generator, "GEN01")

records = [
    {
        "parent_class_id": parent_class_id,
        "parent_object_id": parent_id,
        "collection_id": collection_id,
        "child_class_id": child_class_id,
        "child_object_id": db.get_object_id(ClassEnum.Node, node_name),
    }
    for node_name in node_names
]
db.add_memberships_from_records(records)
```

The `create_membership_record(...)` helper in `plexosdb.utils` builds these
dicts for one parent and many children.

Advantages:

- Single SQLite transaction, much faster than per-row inserts.
- Fails fast with row-index context on the first invalid record.

## Copy pattern

```python
# Duplicate an object and preserve its relationship graph, without
# copying property values. copy_object always copies memberships.
db.copy_object(
    ClassEnum.Generator,
    "GEN01",
    "GEN02",
    copy_properties=False,
)
```

Use this when you need a structurally identical sibling but want to diverge
properties after the clone. `copy_object_memberships(...)` is the standalone
primitive for replicating memberships onto an object you created some other way.

## Query behavior

- `list_object_memberships(...)` returns per-row dicts describing the
  collection, parent object, and child object — useful for diffing what an
  object participates in.
- `list_parent_objects(...)` and `list_child_objects(...)` are the two-way
  traversal primitives; prefer them over hand-written SQL.
- Use `collection_enum` filters in both to narrow the traversal to a single
  relationship type.

## Common mistakes

- Re-adding the `System` membership after `add_object(...)` — it is created
  automatically, and the duplicate raises `AssertionError`.
- Attaching a cross-class property **before** its enabling membership exists,
  then wondering why the property is invisible to PLEXOS.
- Assuming `copy_object(...)` skips memberships — it always copies them; there
  is no `copy_memberships` parameter.
- Using raw strings for class/collection names instead of `ClassEnum` and
  `CollectionEnum`.
- Reaching for `delete_membership(...)` — it is not implemented (raises
  `NotImplementedError`); use `delete_object(...)`, which cascades memberships.

## Related references

- [reference.md](./reference.md) for the base PlexosDB API surface.
- [properties.md](./properties.md) for what to attach _after_ the membership is
  in place.
- [scenarios.md](./scenarios.md) for scenario-tagged overrides.
