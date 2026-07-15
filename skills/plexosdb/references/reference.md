# plexosdb Reference

## When to Use

Use this skill when the task needs concrete plexosdb operations on a `PlexosDB`
instance: inspect classes/collections, navigate objects, mutate memberships and
properties, and round-trip to/from PLEXOS XML.

## Avoid when

- Scope is not a PLEXOS-format model.
- Task is generic SQLite/SQL administration unrelated to PLEXOS schema.

## Additional Reference Documents

- [memberships.md](./memberships.md), parent/child wiring through PLEXOS
  collections.
- [properties.md](./properties.md), single-value and bulk property authoring,
  bands, and text/tag overrides.
- [scenarios.md](./scenarios.md), scenario/variable/datafile/report tags.
- [serialization.md](./serialization.md), XML import/export and schema
  bootstrap.
- [discovery.md](./discovery.md), how to find and validate sources.
- [trigger-prompts.json](../evals/trigger-prompts.json), should-trigger and
  near-miss prompts.
- [bulk-property-records.template.csv](../assets/bulk-property-records.template.csv),
  flat-record CSV template for bulk property authoring.
- [scripts/check_plexos_xml.sh](../scripts/check_plexos_xml.sh), shell-only XML
  sanity check for well-formedness and the expected root element.

## Mental Model

- A `PlexosDB` is a SQLite-backed projection of a PLEXOS XML model.
- Every modeled thing is an **object** that belongs to a **class** and
  (optionally) a **category** within that class.
- Relationships between objects are **memberships** through typed
  **collections** (a collection defines a parent class, a child class, and the
  semantic link).
- Object data lives as **properties** (numeric values with optional bands, date
  ranges, text overrides, and scenario tags) and **attributes** (static
  metadata).
- Use the typed enums `ClassEnum` and `CollectionEnum` from `plexosdb.enums`
  instead of string literals.

## Construction and Schema Bootstrap

```python
from plexosdb import PlexosDB

# Load an existing model
db = PlexosDB.from_xml("model.xml")

# Or bootstrap an empty model and create schema (seed_defaults is
# required before add_object works on a fresh database)
db = PlexosDB()
db.create_schema(seed_defaults=True)
```

For in-depth import/export behavior (including round-trip verification), see
[serialization.md](./serialization.md).

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
- `list_objects_by_class(class_enum, *, category=None) -> list[str]`, object
  names for a class.
- `list_categories(class_enum) -> list[str]`, categories defined under a class.
- `get_object_id(class_enum, name, *, category=None) -> int`, resolves the
  SQLite rowid for a given (class, name[, category]) triple.
- `get_object_properties(class_enum, name, *, property_names=None, scenario=None, category=None)`,
  returns property rows attached to a single object.
- `iterate_properties(class_enum, *, property_names=None, ...)`, streams
  property rows across many objects efficiently.
- `check_object_exists(...)`, `check_property_exists(...)`,
  `check_membership_exists(...)`, and the rest of the `check_*` family are
  side-effect free existence probes.

Behavior notes:

- `get_object_id(...)` raises when the object is missing; wrap in
  `check_object_exists(...)` first if existence is uncertain.
- `list_objects_by_class(...)` returns names only; pair with
  `get_object_id(...)` or `list_object_memberships(...)` for details.
- There is no single `list_components(...)`-style API; navigation is always
  scoped by `ClassEnum`.

## Core Commands You'll Use Most

```python
# Create the hierarchy top-down. add_object also creates the object's
# System membership automatically through its default collection, so
# there is no separate "wire into System" step (a duplicate raises).
db.add_category(ClassEnum.Generator, name="Thermal")
gen_id = db.add_object(
    ClassEnum.Generator, name="GEN01", category="Thermal"
)

# Non-System (cross-class) memberships are explicit; see memberships.md.
# These require the full collection catalog (load via from_xml).

# Author properties (see properties.md for bulk + bands + scenarios)
db.add_property(
    ClassEnum.Generator,
    "GEN01",
    "Max Capacity",
    100.0,
)

# Inspect
props = db.get_object_properties(ClassEnum.Generator, "GEN01")

# Change a value: update_property is not implemented in current plexosdb,
# so delete the existing row and re-add it.
db.delete_property(
    ClassEnum.Generator, "GEN01", property_name="Max Capacity"
)
db.add_property(ClassEnum.Generator, "GEN01", "Max Capacity", 120.0)
db.delete_object(ClassEnum.Generator, name="GEN01")
```

For deeper property authoring and scenario tagging, use
[properties.md](./properties.md) and [scenarios.md](./scenarios.md).

## Object Copy Workflow

```python
# Clone an object with its properties and memberships in one call.
# original_object_name and new_object_name are positional.
db.copy_object(
    ClassEnum.Generator,
    "GEN01",
    "GEN02",
    copy_properties=True,
)

# copy_object already copies memberships. Use copy_object_memberships on
# its own only to replicate memberships onto an object created separately.
db.copy_object_memberships(
    ClassEnum.Generator,
    original_name="GEN01",
    new_name="GEN03",
)
```

## Failure Playbook

- `get_object_id(...)` raises for missing object:
  - Call `check_object_exists(class_enum, name)` first.
  - Cross-check `list_objects_by_class(class_enum)` for typos.
- Property appears not attached after `add_property(...)`:
  - Confirm parent membership exists; many properties require the object to
    belong to a specific collection before the property is valid. See
    [memberships.md](./memberships.md).
  - Use `list_valid_properties(ClassEnum, CollectionEnum, ...)` to check whether
    the property name is valid for that collection.
- XML export disagrees with input:
  - Run `bash scripts/check_plexos_xml.sh <path> [--root MasterDataSet]`.
  - Re-import with `PlexosDB.from_xml(path)` and diff
    `list_objects_by_class(...)` + `iterate_properties(...)` counts.
- SQLite state looks suspicious:
  - Inspect through plexosdb APIs first (`list_*`, `get_*`,
    `iterate_properties`).
  - If API output and expected state disagree, confirm behavior against
    `src/plexosdb/db.py`, `src/plexosdb/checks.py`, and related tests rather
    than using bundled database-inspection scripts.

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

See [serialization.md](./serialization.md) for schema-bootstrap caveats and
PLEXOS-version handling.

## Output Expectations

- What was inspected and how (specific `ClassEnum`/`CollectionEnum` calls).
- What changed at the object/membership/property level.
- How the XML round-trip (or SQLite-only workflow) was verified.
- Which integrated references were consulted and why.
