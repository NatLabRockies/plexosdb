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
- `db.update_scenario(...)` changes a scenario's name, category, or description.
- `db.create_object_scenario(...)` creates a scenario with property values for
  one object, optionally inheriting from a base scenario.

Tag-level APIs (per `data_id`):

- `db.add_datafile_tag(data_id, file_path, *, description=None)`
- `db.add_text(text_class, text_value, data_id)`
- `db.check_tag_exists(data_id, object_id) -> bool`
- `db.add_variable_tag(data_id, variable_name, *, value=None)` links a Variable.
- `db.delete_text(...)` and `db.update_text(...)` manage existing text metadata.

Reports:

- `db.add_report(*, object_name, property, collection, parent_class, child_class, ...)`;
  create the `Report` object first with
  `add_object(ClassEnum.Report, name=...)`.
- `db.list_valid_properties_report(collection_enum, parent_class_enum, child_class_enum)`,
  property names eligible for report output.
- `db.list_reports()` lists configured report rows and their related names.

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

Use `create_object_scenario(...)` to create a new scenario for an object,
optionally copying qualified property rows from `base_scenario` before applying
overrides. It creates new rows rather than retagging existing rows.

## Variable tags

Use `add_variable_tag(data_id, variable_name)` to link an existing Variable to a
property data row. An optional `value` also updates that row's value.

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
invalid property). Use `list_reports()` to inspect configured reports.

## Common mistakes

- Forgetting to wire the scenario into the model — the override exists in the
  database but is inactive for every run.
- Using `update_scenario` to change property values: it changes the scenario's
  name, category, or description. Use `update_property(..., scenario=...)` for
  an existing value or `create_object_scenario(...)` for a new scenario.

## Related references

- [properties.md](./properties.md) for the authoring APIs that accept
  `scenario=`, `variable=`, and `text=`.
- [memberships.md](./memberships.md) for wiring scenarios into models.
- [reference.md](./reference.md) for the base PlexosDB API surface.
