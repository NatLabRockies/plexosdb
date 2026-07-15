# plexosdb Scenarios and Tags Reference

Use this document when authoring scenario-tagged properties, variable overrides,
datafile tags, or report configurations in a `PlexosDB`.

## Scope in this skill

This reference covers:

- creating and inspecting scenarios
- attaching scenario tags to existing property rows
- variable tags and datafile tags (generic override mechanisms)
- report authoring and listing
- model → scenario association queries

## Core APIs

Scenarios:

- `db.add_scenario(name, category=None) -> int`
- `db.list_scenarios() -> list[str]`
- `db.list_scenarios_by_model(model_name) -> list[str]`
- `db.list_models() -> list[str]`
- `db.get_scenario_id(name) -> int`
- `db.check_scenario_exists(name) -> bool`
- `db.update_scenario(...)` and `db.create_object_scenario(...)` are not
  implemented in current plexosdb (both raise `NotImplementedError`). Create
  scenario-tagged values with `add_property(..., scenario=...)`.

Tag-level APIs (per `data_id`):

- `db.add_datafile_tag(data_id, file_path, *, description=None)`
- `db.add_text(text_class, text_value, data_id)`
- `db.check_tag_exists(data_id, object_id) -> bool`
- `db.add_variable_tag(...)`, `db.delete_text(...)`, and `db.update_text(...)`
  are not implemented in current plexosdb (they raise `NotImplementedError`).

Reports:

- `db.add_report(*, object_name, property, collection, parent_class, child_class, ...)`;
  create the `Report` object first with
  `add_object(ClassEnum.Report, name=...)`.
- `db.list_valid_properties_report(collection_enum, parent_class_enum, child_class_enum)`,
  property names eligible for report output.
- `db.list_reports()` is not implemented in current plexosdb (raises
  `NotImplementedError`).

## What is a scenario

A **scenario** is a named group of property overrides. When PLEXOS runs a model,
it applies the scenarios assigned to that model; for every property that has a
matching scenario-tagged row, the tagged value overrides the base value.
Properties without a scenario tag are always active.

Key implications:

- Adding a scenario-tagged property **does not** remove the base value.
- Multiple scenarios can coexist on the same property name; PLEXOS resolves by
  which scenarios are attached to the running model.

## Recommended path

1. Create the scenario:
   ```python
   db.add_scenario("Low_Demand")
   ```
2. Attach scenario-tagged property rows (preferred: through
   `add_property(..., scenario="Low_Demand")`, see
   [properties.md](./properties.md)):
   ```python
   db.add_property(
       ClassEnum.Generator, "GEN01", "Max Capacity", 80.0,
       scenario="Low_Demand",
   )
   ```
3. Attach the scenario to a model (through the `Model` object's memberships; see
   [memberships.md](./memberships.md)):
   ```python
   db.add_membership(
       parent_class_enum=ClassEnum.Model,
       parent_object_name="BaseModel",
       child_class_enum=ClassEnum.Scenario,
       child_object_name="Low_Demand",
       collection_enum=CollectionEnum.Scenarios,
   )
   ```

## Adding a scenario-tagged value

Create the scenario-tagged value directly with `add_property(..., scenario=...)`
— a tagged row coexists with the base row rather than replacing it:

```python
db.add_property(
    ClassEnum.Generator, "GEN02", "Max Capacity", 60.0,
    scenario="Low_Demand",
)
```

Retagging an existing row in place (`create_object_scenario`) is not implemented
in current plexosdb.

## Variable tags

`add_variable_tag(...)` is not implemented in current plexosdb (it raises
`NotImplementedError`). Until it lands, drive time- or scenario-varying values
through scenario-tagged properties (`add_property(..., scenario=...)`) or
datafile-backed properties (`datafile_text=`, below).

## Datafile tags

Use `add_datafile_tag(...)` to bind a property to a `DataFile` object whose own
properties describe the CSV/timeseries source.

```python
# Attach the CSV path directly to the consuming property
db.add_property(
    ClassEnum.Region, "REGION_WEST", "Load", 0.0,
    datafile_text="inputs/load_profile.csv",
)

# Or link a property row to an existing DataFile object by file path
data_id = db.add_property(ClassEnum.Region, "REGION_WEST", "Load", 0.0)
db.add_datafile_tag(data_id, "inputs/load_profile.csv")
```

`add_datafile_tag(data_id, file_path)` matches an existing `DataFile` object
whose `Filename` property equals `file_path`.

## Inspection queries

```python
# Which scenarios exist at all
db.list_scenarios()

# Which scenarios does a given model use
db.list_scenarios_by_model("BaseModel")

# Inspect scenario-tagged properties on an object
rows = db.get_object_properties(
    ClassEnum.Generator, "GEN01", scenario="Low_Demand"
)
```

## Reports

Reports are attached via `add_report(...)`:

```python
# Create the Report object, then configure the report row.
db.add_object(ClassEnum.Report, name="GenerationReport")
db.add_report(
    object_name="GenerationReport",
    property="Generation",
    collection=CollectionEnum.Generators,
    parent_class=ClassEnum.System,
    child_class=ClassEnum.Generator,
)

# Check eligible report properties (collection first, then parent/child)
db.list_valid_properties_report(
    CollectionEnum.Generators,
    ClassEnum.System,
    ClassEnum.Generator,
)
```

Use `list_valid_properties_report(...)` before adding a report to avoid
attaching an ineligible property name (`add_report` raises `NameError` on an
invalid property). `list_reports()` is not implemented in current plexosdb.

## Common mistakes

- Creating a scenario-tagged property without first creating the scenario object
  itself (`add_scenario(...)`). The tagged property is accepted into SQLite but
  has no anchor in the scenarios table.
- Forgetting to wire the scenario into the model — the override exists in the
  database but is inactive for every run.
- Reaching for `update_scenario`, `create_object_scenario`, or `update_property`
  to edit scenario values — all are stubs. Create new tagged rows with
  `add_property(..., scenario=...)` and remove old ones with
  `delete_property(..., scenario=...)`.

## Related references

- [properties.md](./properties.md) for the authoring APIs that accept
  `scenario=`, `variable=`, and `text=`.
- [memberships.md](./memberships.md) for wiring scenarios into models.
- [reference.md](./reference.md) for the base PlexosDB API surface.
