# plexosdb Reference

## When to Use

Use this skill when the task needs concrete plexosdb operations on a
`PlexosDB` instance: inspect classes/collections, navigate objects,
mutate memberships and properties, and round-trip to/from PLEXOS XML.

## Avoid when

- Scope is not a PLEXOS-format model.
- Task is generic SQLite/SQL administration unrelated to PLEXOS schema.

## Additional Reference Documents

- [MEMBERSHIPS.md](./MEMBERSHIPS.md), parent/child wiring through PLEXOS
  collections.
- [PROPERTIES.md](./PROPERTIES.md), single-value and bulk property
  authoring, bands, and text/tag overrides.
- [SCENARIOS.md](./SCENARIOS.md), scenario/variable/datafile/report tags.
- [SERIALIZATION.md](./SERIALIZATION.md), XML import/export and schema
  bootstrap.
- [DISCOVERY.md](./DISCOVERY.md), how to find and validate sources.
- [EXAMPLES.md](./EXAMPLES.md), should-trigger and near-miss prompts.
- [scripts/check_api_symbols.py](./scripts/check_api_symbols.py),
  optional API drift checker.
- [scripts/check_plexos_xml.sh](./scripts/check_plexos_xml.sh),
  well-formed XML + root-element check.
- [scripts/inspect_plexos_db.py](./scripts/inspect_plexos_db.py), SQLite
  table counts and sample rows.

## Mental Model

- A `PlexosDB` is a SQLite-backed projection of a PLEXOS XML model.
- Every modeled thing is an **object** that belongs to a **class** and
  (optionally) a **category** within that class.
- Relationships between objects are **memberships** through typed
  **collections** (a collection defines a parent class, a child class,
  and the semantic link).
- Object data lives as **properties** (numeric values with optional
  bands, date ranges, text overrides, and scenario tags) and
  **attributes** (static metadata).
- Use the typed enums `ClassEnum` and `CollectionEnum` from
  `plexosdb.enums` instead of string literals.

## Construction and Schema Bootstrap

```python
from plexosdb import PlexosDB

# Load an existing model
db = PlexosDB.from_xml("model.xml")

# Or bootstrap an empty model and create schema
db = PlexosDB()
db.create_schema()
```

For in-depth import/export behavior (including round-trip verification),
see [SERIALIZATION.md](./SERIALIZATION.md).

## Navigation and Inspection Commands

```python
from plexosdb import PlexosDB, ClassEnum, CollectionEnum

db = PlexosDB.from_xml("model.xml")

# Top-level inventory
classes = db.list_classes()
collections = db.list_collections(class_enum=ClassEnum.Generator)
categories = db.list_categories(ClassEnum.Generator)
scenarios = db.list_scenarios()
models = db.list_models()

# Objects for a class (optionally scoped to category)
gen_names = db.list_objects_by_class(ClassEnum.Generator)
gen_names_by_cat = db.list_objects_by_class(
    ClassEnum.Generator, category="Thermal"
)

# Resolve typed IDs
class_id = db.get_class_id(ClassEnum.Generator)
collection_id = db.get_collection_id(
    CollectionEnum.Generators,
    parent_class_enum=ClassEnum.System,
    child_class_enum=ClassEnum.Generator,
)
gen_id = db.get_object_id(ClassEnum.Generator, "GEN01")
```

## Core API Contracts (high-signal behavior)

- `list_classes() -> list[str]`, all classes present in the database.
- `list_collections(class_enum=..., parent_class_enum=...) -> list[...]`,
  collections filtered by child and optional parent class.
- `list_objects_by_class(class_enum, *, category=None) -> list[str]`,
  object names for a class.
- `list_categories(class_enum) -> list[str]`, categories defined under
  a class.
- `get_object_id(class_enum, name, *, category=None) -> int`, resolves
  the SQLite rowid for a given (class, name[, category]) triple.
- `get_object_properties(class_enum, name, *, property_names=None,
  scenario=None, category=None)`, returns property rows attached to a
  single object.
- `iterate_properties(class_enum, *, property_names=None, ...)`, streams
  property rows across many objects efficiently.
- `check_object_exists(...)`, `check_property_exists(...)`,
  `check_membership_exists(...)`, and the rest of the `check_*` family
  are side-effect free existence probes.

Behavior notes:

- `get_object_id(...)` raises when the object is missing; wrap in
  `check_object_exists(...)` first if existence is uncertain.
- `list_objects_by_class(...)` returns names only; pair with
  `get_object_id(...)` or `list_object_memberships(...)` for details.
- There is no single `list_components(...)`-style API; navigation is
  always scoped by `ClassEnum`.

## Core Commands You'll Use Most

```python
# Create the hierarchy top-down
db.add_category(ClassEnum.Generator, name="Thermal")
gen_id = db.add_object(
    ClassEnum.Generator, name="GEN01", category="Thermal"
)

# Wire memberships (see MEMBERSHIPS.md for full patterns)
db.add_membership(
    parent_class_enum=ClassEnum.System,
    parent_object_name="System",
    child_class_enum=ClassEnum.Generator,
    child_object_name="GEN01",
    collection_enum=CollectionEnum.Generators,
)

# Author properties (see PROPERTIES.md for bulk + bands + scenarios)
db.add_property(
    ClassEnum.Generator,
    "GEN01",
    "Max Capacity",
    100.0,
)

# Inspect
props = db.get_object_properties(ClassEnum.Generator, "GEN01")

# Update / delete
db.update_property(
    ClassEnum.Generator, "GEN01", "Max Capacity", 120.0,
)
db.delete_object(ClassEnum.Generator, name="GEN01")
```

For deeper property authoring and scenario tagging, use
[PROPERTIES.md](./PROPERTIES.md) and [SCENARIOS.md](./SCENARIOS.md).

## Object Copy Workflow

```python
# Clone object and all of its properties and memberships
db.copy_object(
    ClassEnum.Generator,
    original_name="GEN01",
    new_name="GEN02",
    copy_properties=True,
)
db.copy_object_memberships(
    ClassEnum.Generator,
    original_name="GEN01",
    new_name="GEN02",
)
```

## Failure Playbook

- `get_object_id(...)` raises for missing object:
  - Call `check_object_exists(class_enum, name)` first.
  - Cross-check `list_objects_by_class(class_enum)` for typos.
- Property appears not attached after `add_property(...)`:
  - Confirm parent membership exists; many properties require the
    object to belong to a specific collection before the property is
    valid. See [MEMBERSHIPS.md](./MEMBERSHIPS.md).
  - Use `list_valid_properties(ClassEnum, CollectionEnum, ...)` to
    check whether the property name is valid for that collection.
- XML export disagrees with input:
  - Run `bash scripts/check_plexos_xml.sh <path> [--root MasterDataSet]`.
  - Re-import with `PlexosDB.from_xml(path)` and diff
    `list_objects_by_class(...)` + `iterate_properties(...)` counts.
- SQLite state looks suspicious:
  - Run `uvx --from python python scripts/inspect_plexos_db.py <db.sqlite>
    [--sample N]`.

## Persistence

```python
# Export back to PLEXOS XML
db.to_xml("model_out.xml")

# Round-trip check
reloaded = PlexosDB.from_xml("model_out.xml")
assert len(reloaded.list_objects_by_class(ClassEnum.Generator)) == len(
    db.list_objects_by_class(ClassEnum.Generator)
)
```

See [SERIALIZATION.md](./SERIALIZATION.md) for schema-bootstrap caveats
and PLEXOS-version handling.

## Output Expectations

- What was inspected and how (specific `ClassEnum`/`CollectionEnum`
  calls).
- What changed at the object/membership/property level.
- How the XML round-trip (or SQLite-only workflow) was verified.
- Which integrated references were consulted and why.
