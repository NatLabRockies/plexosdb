# plexosdb Properties Reference

Use this document for authoring, inspecting, updating, and bulk-loading PLEXOS
properties in a `PlexosDB`.

## Scope in this skill

This reference covers:

- single-value property authoring (`add_property`)
- bulk property authoring from records (`add_properties_from_records`)
- optional fields: `scenario`, `band`, `date_from`, `date_to`, `datafile_text`,
  `timeslice`
- property listing and iteration (`get_object_properties`, `iterate_properties`)
- updating and deleting properties
- validating a property name against a collection (`list_valid_properties`)

For scenario-specific tagging and variable/datafile overrides, see
[scenarios.md](./scenarios.md).

## Mental Model

A **property** is a (possibly scenario-tagged) value attached to a
**membership** (see [memberships.md](./memberships.md)). A property has:

- a name defined by the collection (e.g., `"Max Capacity"`, `"Heat Rate"`,
  `"VoM Charge"`).
- a numeric `value`.
- an optional `band` (integer, for banded curves like heat rate).
- an optional date range (`date_from`, `date_to`).
- an optional `scenario` tag that makes the value active only under that
  scenario.
- an optional `datafile_text` path (for datafile-backed properties such as
  time-series inputs).

## Core APIs

- `db.add_property(object_class_enum, object_name, property_name, value, *, scenario=None, band=None, date_from=None, date_to=None, datafile_text=None, timeslice=None, collection_enum=None, parent_class_enum=None, parent_object_name=None) -> int`,
  adds a single property row and returns its `data_id`.
- `db.add_properties_from_records(records, *, object_class, collection, scenario, parent_class=ClassEnum.System)`,
  bulk path (see "Bulk insert pattern" for the record shape).
- `db.get_object_properties(class_enum, name, property_names=None, *, parent_class_enum=None, collection_enum=None, category=None, scenario=None) -> list[PropertyRecord]`,
  returns the property rows attached to a single object.
- `db.iterate_properties(*, class_enum=None, object_names=None, property_names=None, ...) -> Iterator[PropertyRecord]`,
  streams property rows across many objects (preferred for large models).
- `db.update_property(...)` and `db.update_properties(...)` are not implemented
  in current plexosdb (both raise `NotImplementedError`). To change a value,
  `delete_property(...)` the row and re-add it.
- `db.delete_property(object_class, object_name, *, property_name, scenario=None, collection=None, parent_class=None, parent_object_name=None)`,
  removes a property row.
- `db.list_valid_properties(collection_enum, parent_class_enum, child_class_enum) -> list[str]`,
  enumerates valid property names for a collection (collection is the first,
  positional-only argument).
- `db.check_property_exists(...) -> bool`, safe existence probe.
- `db.add_band(data_id, band_id, *, state=None)` and
  `db.add_datafile_tag(data_id, file_path, *, description=None)` for lower-level
  overrides. `db.add_text(text_class, text_value, data_id)` attaches a text
  override. `db.add_variable_tag(...)` is not implemented (raises
  `NotImplementedError`).

## Single-value pattern

```python
from plexosdb import PlexosDB, ClassEnum

db = PlexosDB()
db.create_schema(seed_defaults=True)

# add_object also creates the System membership; do not add it again.
db.add_object(ClassEnum.Generator, "GEN01")

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

- `scenario` does not replace the base row; it adds a scenario-tagged override.
  PLEXOS picks the scenario-tagged value when that scenario is active and falls
  back to the untagged value otherwise.
- `band` is required when a property is defined as banded by the collection
  (e.g., heat-rate curves). Omitting the band on such a property is a frequent
  source of silent data loss.

## Bulk insert pattern

```python
records = [
    {"name": "GEN01", "property": "Max Capacity", "value": 100.0},
    {"name": "GEN01", "property": "Min Stable Level", "value": 20.0},
    {"name": "GEN02", "property": "Max Capacity", "value": 60.0},
]
db.add_properties_from_records(
    records,
    object_class=ClassEnum.Generator,
    collection=CollectionEnum.Generators,
    scenario="Base Case",
)
```

Each record is a flat dict
`{"name": <object_name>, "property": <PropertyName>, "value": <v>}` (optional
`band`, `date_from`, `date_to`, `datafile_text`, and `timeslice` keys attach
detail). `object_class`, `collection`, and `scenario` are required keyword
arguments (`parent_class` defaults to `ClassEnum.System`). Use
[bulk-property-records.template.csv](../assets/bulk-property-records.template.csv)
when preparing CSV-backed records. A nested `{"name": ..., "properties": {...}}`
payload still works but is deprecated.

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

`iterate_properties` is the right primitive for feeding downstream analyses;
prefer it to repeated `get_object_properties(...)` calls.

## Updating and deleting

```python
# update_property / update_properties are not implemented in current
# plexosdb. To change a value, delete the existing row and re-add it.
db.delete_property(
    ClassEnum.Generator, "GEN01", property_name="Max Capacity"
)
db.add_property(ClassEnum.Generator, "GEN01", "Max Capacity", 120.0)

# Delete a scenario-tagged override (scoped by scenario)
db.delete_property(
    ClassEnum.Generator,
    "GEN01",
    property_name="Max Capacity",
    scenario="Low_Demand",
)
```

`delete_property` takes `property_name` (and optional `scenario`) as keyword
arguments; it removes the row and its tags/text.

## Validation

- `list_valid_properties(CollectionEnum.Generators, ClassEnum.System, ClassEnum.Generator)`
  returns every property name PLEXOS recognizes for that collection (collection
  first, then parent and child class). Use this when a property append fails
  with an unknown-name error.
- `check_property_exists(...)` is a safe existence probe before update/delete.

## Text, variables, datafiles

- Attach a CSV/time-series path directly to the property that consumes it via
  the `datafile_text` parameter — this is the common path:
  ```python
  db.add_property(
      ClassEnum.Generator, "GEN01", "Rating", 0.0,
      band=1, datafile_text="inputs/gen_profile.csv",
  )
  ```
- `add_text(text_class, text_value, data_id)` attaches a lower-level text
  override to an existing property `data_id`.
- `add_datafile_tag(data_id, file_path)` links a property row to a `DataFile`
  object whose `Filename` matches `file_path`.
- `add_variable_tag(...)` is not implemented in current plexosdb (raises
  `NotImplementedError`).

## Common mistakes

- Re-adding the System membership after `add_object(...)`; it is automatic and a
  duplicate raises (see [memberships.md](./memberships.md)).
- Forgetting `band=` for banded curves, causing duplicate-row collisions on
  subsequent inserts.
- Reaching for `update_property`/`update_properties` — both are stubs; delete
  the row and re-add it, and use `add_property(..., scenario=...)` for new
  scenario overrides.
- Running `add_property` in a per-row loop for thousands of rows instead of
  batching with `add_properties_from_records`.

## Related references

- [reference.md](./reference.md) for base navigation APIs.
- [memberships.md](./memberships.md) for the prerequisite wiring.
- [scenarios.md](./scenarios.md) for scenario/variable/datafile tags in depth.
