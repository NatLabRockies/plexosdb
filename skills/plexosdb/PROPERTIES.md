# plexosdb Properties Reference

Use this document for authoring, inspecting, updating, and bulk-loading
PLEXOS properties in a `PlexosDB`.

## Scope in this skill

This reference covers:

- single-value property authoring (`add_property`)
- bulk property authoring from records (`add_properties_from_records`)
- optional fields: `band`, `date_from`, `date_to`, `scenario`,
  `variable`, `text`, `action`
- property listing and iteration (`get_object_properties`,
  `iterate_properties`)
- updating and deleting properties
- validating a property name against a collection
  (`list_valid_properties`)

For scenario-specific tagging and variable/datafile overrides, see
[SCENARIOS.md](./SCENARIOS.md).

## Mental Model

A **property** is a (possibly scenario-tagged) value attached to a
**membership** (see [MEMBERSHIPS.md](./MEMBERSHIPS.md)). A property has:

- a name defined by the collection (e.g., `"Max Capacity"`,
  `"Heat Rate"`, `"VoM Charge"`).
- a numeric `value`.
- an optional `band` (integer, for banded curves like heat rate).
- an optional date range (`date_from`, `date_to`).
- an optional `scenario` tag that makes the value active only under that
  scenario.
- an optional `text` override (for string-valued properties like
  datafile paths) and/or a `variable` tag.

## Core APIs

- `db.add_property(class_enum, object_name, property_name, value,
  *, band=None, date_from=None, date_to=None, scenario=None,
  variable=None, text=None, action=None) -> int`, adds a single
  property row and returns its `data_id`.
- `db.add_properties_from_records(records, collection_enum=None,
  parent_class_enum=None)`, bulk path.
- `db.get_object_properties(class_enum, name, *, property_names=None,
  scenario=None, category=None) -> list[PropertyRecord]`, returns the
  property rows attached to a single object.
- `db.iterate_properties(class_enum, *, property_names=None, ...)`,
  streams property rows across many objects (preferred for large
  models).
- `db.update_property(class_enum, object_name, property_name, value,
  *, band=None, scenario=None, ...)`, updates an existing property.
- `db.update_properties(updates)`, bulk update path taking a list of
  dicts (each dict must resolve to one row via its filter keys).
- `db.delete_property(class_enum, object_name, property_name, *,
  band=None, scenario=None, ...)`.
- `db.list_valid_properties(class_enum, collection_enum, *,
  parent_class_enum=None) -> list[str]`, enumerates valid property
  names for the given collection.
- `db.check_property_exists(class_enum, object_name, property_name,
  *, band=None, scenario=None, ...) -> bool`.
- `db.add_band(...)`, `db.add_text(...)`, `db.add_variable_tag(...)`,
  `db.add_datafile_tag(...)` for lower-level overrides.

## Single-value pattern

```python
from plexosdb import PlexosDB, ClassEnum

db = PlexosDB()
db.create_schema()
db.add_object(ClassEnum.Generator, "GEN01")
db.add_membership(
    parent_class_enum=ClassEnum.System,
    parent_object_name="System",
    child_class_enum=ClassEnum.Generator,
    child_object_name="GEN01",
    collection_enum=CollectionEnum.Generators,
)

db.add_property(ClassEnum.Generator, "GEN01", "Max Capacity", 100.0)
db.add_property(
    ClassEnum.Generator,
    "GEN01",
    "Heat Rate",
    10.5,
    band=1,
)
db.add_property(
    ClassEnum.Generator,
    "GEN01",
    "Max Capacity",
    80.0,
    scenario="Low_Demand",
)
```

Notes:

- `scenario` does not replace the base row; it adds a scenario-tagged
  override. PLEXOS picks the scenario-tagged value when that scenario
  is active and falls back to the untagged value otherwise.
- `band` is required when a property is defined as banded by the
  collection (e.g., heat-rate curves). Omitting the band on such a
  property is a frequent source of silent data loss.

## Bulk insert pattern

```python
records = [
    {
        "object_name": "GEN01",
        "property_name": "Max Capacity",
        "value": 100.0,
    },
    {
        "object_name": "GEN01",
        "property_name": "Heat Rate",
        "value": 10.5,
        "band": 1,
    },
    {
        "object_name": "GEN02",
        "property_name": "Max Capacity",
        "value": 60.0,
        "scenario": "Low_Demand",
    },
]
db.add_properties_from_records(
    records,
    collection_enum=CollectionEnum.Generators,
    parent_class_enum=ClassEnum.System,
)
```

Why prefer this over per-row `add_property`:

- Wraps inserts in a single transaction for large batches.
- Validates property names once against the target collection.
- Reports the first invalid record with enough context to fix it.

## Listing and iteration

```python
# One object
rows = db.get_object_properties(ClassEnum.Generator, "GEN01")
cap_rows = db.get_object_properties(
    ClassEnum.Generator, "GEN01", property_names=["Max Capacity"]
)

# Many objects efficiently
for row in db.iterate_properties(
    ClassEnum.Generator,
    property_names=["Max Capacity", "Heat Rate"],
):
    print(row)
```

`iterate_properties` is the right primitive for feeding downstream
analyses; prefer it to repeated `get_object_properties(...)` calls.

## Updating and deleting

```python
# Change the base value
db.update_property(
    ClassEnum.Generator, "GEN01", "Max Capacity", 120.0
)

# Change a scenario override only
db.update_property(
    ClassEnum.Generator,
    "GEN01",
    "Max Capacity",
    90.0,
    scenario="Low_Demand",
)

# Remove a banded entry
db.delete_property(
    ClassEnum.Generator, "GEN01", "Heat Rate", band=1
)
```

For bulk updates:

```python
db.update_properties([
    {
        "class_enum": ClassEnum.Generator,
        "object_name": "GEN01",
        "property_name": "Max Capacity",
        "value": 120.0,
    },
    {
        "class_enum": ClassEnum.Generator,
        "object_name": "GEN02",
        "property_name": "Max Capacity",
        "value": 60.0,
        "scenario": "Low_Demand",
    },
])
```

Each update dict must resolve to exactly one row; ambiguous filter
keys raise an error.

## Validation

- `list_valid_properties(ClassEnum.Generator, CollectionEnum.Generators,
  parent_class_enum=ClassEnum.System)` returns every property name
  PLEXOS recognizes for that collection. Use this when a property
  append fails with an unknown-name error.
- `check_property_exists(...)` is a safe existence probe before
  update/delete.

## Text, variables, datafiles

- `add_text(data_id, text, class_enum=...)` attaches a string override
  to a numeric property (for example, a CSV path associated with a
  `Generator` `Heat Rate` curve).
- `add_variable_tag(data_id, variable_name)` marks a property value as
  sourced from a PLEXOS variable.
- `add_datafile_tag(data_id, datafile_name)` marks the property as
  sourced from a datafile object — pair with a `DataFile` object and
  its own properties.

These are lower-level APIs; most agent tasks should prefer the
equivalent `add_property(..., text=..., variable=...)` convenience
parameters.

## Common mistakes

- Attaching a property before the parent membership exists (see
  [MEMBERSHIPS.md](./MEMBERSHIPS.md)).
- Forgetting `band=` for banded curves, causing duplicate-row collisions
  on subsequent inserts.
- Using `update_property` to create a new scenario override — it will
  raise unless the base+scenario row already exists; use
  `add_property(..., scenario=...)` for new overrides.
- Running `add_property` in a per-row loop for thousands of rows
  instead of batching with `add_properties_from_records`.

## Related references

- [REFERENCE.md](./REFERENCE.md) for base navigation APIs.
- [MEMBERSHIPS.md](./MEMBERSHIPS.md) for the prerequisite wiring.
- [SCENARIOS.md](./SCENARIOS.md) for scenario/variable/datafile tags in
  depth.
