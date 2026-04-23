# plexosdb Scenarios and Tags Reference

Use this document when authoring scenario-tagged properties, variable
overrides, datafile tags, or report configurations in a `PlexosDB`.

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
- `db.update_scenario(...)`
- `db.create_object_scenario(...)`, attaches a named scenario as the
  active tag for an already-existing property row.

Tag-level APIs (per `data_id`):

- `db.add_datafile_tag(data_id, datafile_name)`
- `db.add_variable_tag(data_id, variable_name)`
- `db.add_text(data_id, text, class_enum=...)`
- `db.delete_text(data_id, class_enum=...)`
- `db.update_text(data_id, text, class_enum=...)`
- `db.check_tag_exists(data_id, object_id) -> bool`

Reports:

- `db.add_report(name, ...)`
- `db.list_reports() -> list[dict]`
- `db.list_valid_properties_report(...)`, property names eligible for
  report output.

## What is a scenario

A **scenario** is a named group of property overrides. When PLEXOS runs
a model, it applies the scenarios assigned to that model; for every
property that has a matching scenario-tagged row, the tagged value
overrides the base value. Properties without a scenario tag are always
active.

Key implications:

- Adding a scenario-tagged property **does not** remove the base value.
- Multiple scenarios can coexist on the same property name; PLEXOS
  resolves by which scenarios are attached to the running model.

## Recommended path

1. Create the scenario:
   ```python
   db.add_scenario("Low_Demand")
   ```
2. Attach scenario-tagged property rows (preferred: through
   `add_property(..., scenario="Low_Demand")`, see
   [PROPERTIES.md](./PROPERTIES.md)):
   ```python
   db.add_property(
       ClassEnum.Generator, "GEN01", "Max Capacity", 80.0,
       scenario="Low_Demand",
   )
   ```
3. Attach the scenario to a model (through the `Model` object's
   memberships; see [MEMBERSHIPS.md](./MEMBERSHIPS.md)):
   ```python
   db.add_membership(
       parent_class_enum=ClassEnum.Model,
       parent_object_name="BaseModel",
       child_class_enum=ClassEnum.Scenario,
       child_object_name="Low_Demand",
       collection_enum=CollectionEnum.Scenarios,
   )
   ```

## Retagging an existing property row

When the override already exists as a base row and you want to promote
it into a scenario-tagged row, use `create_object_scenario(...)` with
the property's `data_id`:

```python
data_id = db.add_property(
    ClassEnum.Generator, "GEN02", "Max Capacity", 60.0
)
db.create_object_scenario(data_id, scenario="Low_Demand")
```

Prefer the single-call `add_property(..., scenario=...)` path unless
you specifically need to retag a pre-existing row.

## Variable tags

Use `add_variable_tag(...)` to mark a numeric property as sourced from a
PLEXOS variable (dynamic curves, interpolated series, etc.). The
variable object itself must exist as an object of class
`ClassEnum.Variable`.

```python
var_id = db.add_object(ClassEnum.Variable, "LOAD_2030")
data_id = db.add_property(
    ClassEnum.Region, "REGION_WEST", "Load", 0.0
)
db.add_variable_tag(data_id, "LOAD_2030")
```

Why use a variable tag instead of raw scenario overrides:

- One variable definition can drive many properties.
- Variables can themselves carry shape/time information that does not
  belong on the individual property.

## Datafile tags

Use `add_datafile_tag(...)` to bind a property to a `DataFile` object
whose own properties describe the CSV/timeseries source.

```python
db.add_object(ClassEnum.DataFile, "load_profile.csv")
db.add_property(
    ClassEnum.DataFile, "load_profile.csv",
    "Filename", 0.0, text="inputs/load_profile.csv",
)
data_id = db.add_property(
    ClassEnum.Region, "REGION_WEST", "Load", 0.0
)
db.add_datafile_tag(data_id, "load_profile.csv")
```

Pair this with a `text` override on the datafile object so PLEXOS
resolves the path on read.

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
db.add_report(
    name="GenerationReport",
    class_enum=ClassEnum.Generator,
    collection_enum=CollectionEnum.Generators,
    parent_class_enum=ClassEnum.System,
    property="Generation",
)

db.list_reports()
db.list_valid_properties_report(
    class_enum=ClassEnum.Generator,
    collection_enum=CollectionEnum.Generators,
)
```

Use `list_valid_properties_report(...)` before adding a report to avoid
attaching an ineligible property name.

## Common mistakes

- Creating a scenario-tagged property without first creating the
  scenario object itself (`add_scenario(...)`). The tagged property is
  accepted into SQLite but has no anchor in the scenarios table.
- Forgetting to wire the scenario into the model — the override exists
  in the database but is inactive for every run.
- Using `scenario=` on `update_property` to *create* a new override;
  use `add_property(..., scenario=...)` for new rows and
  `update_property(..., scenario=...)` only to edit an existing
  scenario-tagged row.
- Mixing variable tags and scenario tags on the same row — pick one
  override mechanism per property.

## Related references

- [PROPERTIES.md](./PROPERTIES.md) for the authoring APIs that accept
  `scenario=`, `variable=`, and `text=`.
- [MEMBERSHIPS.md](./MEMBERSHIPS.md) for wiring scenarios into models.
- [REFERENCE.md](./REFERENCE.md) for the base PlexosDB API surface.
