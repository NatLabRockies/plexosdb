# Tutorial

This tutorial provides a step-by-step introduction to PlexosDB, guiding you
through the essential concepts and operations for working with PLEXOS energy
market simulation models.

## Prerequisites

Before starting this tutorial, ensure you have:

- Python 3.7 or higher installed
- PlexosDB installed (see [Installation](installation.md))
- Basic understanding of energy market modeling concepts

## Learning Objectives

By the end of this tutorial, you will be able to:

- Create and initialize a PlexosDB database
- Import data from PLEXOS XML files
- Add objects and properties to your model
- Query the database for information
- Work with scenarios and model configurations

## Creating Your First Database

Let's start by creating a new PlexosDB database:

```python
from plexosdb import PlexosDB

# Create a new in-memory database
db = PlexosDB()

# Initialize schema + minimal defaults for object workflows
db.create_schema(seed_defaults=True)
```

This creates an in-memory database with the PLEXOS schema and minimal lookup
data so object APIs work immediately.

If you call `db.create_schema()` without `seed_defaults=True`, only the table
structure is created. For `add_object(...)` and related workflows, use
`seed_defaults=True`, import from XML, or provide a custom seeded schema.

### create_schema options: seed_defaults and schema

`create_schema` supports two useful parameters:

- `seed_defaults=True`: seeds minimal classes/collections/System object so
  methods like `add_object` work immediately on a fresh database.
- `schema="..."`: execute custom SQL schema content directly from a string.
- `version="..."`: updates `t_config.Version` (default `"9.2"`) when that row
  exists in schema data. Use `version=None` when schema setup is followed by XML
  import that provides its own version.

```python
from plexosdb import PlexosDB
from plexosdb.enums import ClassEnum

db = PlexosDB()
db.create_schema(seed_defaults=True)

# Works immediately because defaults were seeded
db.add_object(ClassEnum.Generator, "Generator1")

# Set a specific DB version when creating from schema
db.create_schema(seed_defaults=True, version="11.0")
```

Custom schema string example (copy/paste):

```python
from plexosdb import PlexosDB
from plexosdb.enums import ClassEnum

schema = """
CREATE TABLE IF NOT EXISTS t_config (
    element TEXT PRIMARY KEY,
    value   TEXT
);

CREATE TABLE IF NOT EXISTS t_class (
    class_id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    is_enabled INTEGER
);

CREATE TABLE IF NOT EXISTS t_category (
    category_id INTEGER PRIMARY KEY,
    class_id INTEGER,
    name TEXT,
    rank INTEGER
);

CREATE TABLE IF NOT EXISTS t_object (
    object_id INTEGER PRIMARY KEY,
    name TEXT,
    class_id INTEGER,
    category_id INTEGER,
    GUID TEXT,
    description TEXT
);

INSERT INTO t_class(class_id, name, description, is_enabled)
VALUES (1, 'System', 'System class', 1),
       (2, 'Generator', 'Generator class', 1);

INSERT INTO t_category(category_id, class_id, name, rank)
VALUES (1, 1, '-', 1),
       (2, 2, '-', 1);

INSERT INTO t_object(object_id, name, class_id, category_id, GUID)
VALUES (1, 'System', 1, 1, '00000000-0000-0000-0000-000000000001');
"""

db = PlexosDB()
db.create_schema(schema=schema)

# The schema string can be as small or as complete as your workflow requires.
```

## Working with Objects

Objects represent entities in your energy model such as generators, nodes, and
regions.

### Adding Objects

```python
from plexosdb.enums import ClassEnum

# Add a generator to the database
db.add_object(ClassEnum.Generator, "Generator1")

# Add a node with additional details
db.add_object(ClassEnum.Node, "Node1", description="Main transmission node")

# Verify objects were added
generators = db.list_objects_by_class(ClassEnum.Generator)
print(f"Generators: {generators}")
```

### Adding Properties

Properties define characteristics of objects like capacity, cost, or operational
parameters:

```python
# Add capacity property to the generator
db.add_property(
    ClassEnum.Generator,
    "Generator1",
    "Max Capacity",
    500.0  # MW
)

# Add multiple properties
db.add_property(ClassEnum.Generator, "Generator1", "Min Stable Level", 100.0)
db.add_property(ClassEnum.Generator, "Generator1", "Heat Rate", 9500.0)
```

### Querying Properties

Retrieve property information for specific objects:

```python
# Get all properties for Generator1
properties = db.get_object_properties(ClassEnum.Generator, "Generator1")

for prop in properties:
    print(f"{prop['property']}: {prop['value']} {prop['unit'] or ''}")
```

## Working with XML Files

PlexosDB can import existing PLEXOS XML files and export databases back to XML
format.

### Importing from XML

```python
# Create database from existing XML file
db = PlexosDB.from_xml("/path/to/your/plexos_model.xml")

# List all generators in the imported model
generators = db.list_objects_by_class(ClassEnum.Generator)
print(f"Found {len(generators)} generators in the model")
```

### Exporting to XML

```python
# Export your database to XML format
db.to_xml("/path/to/output_model.xml")
```

## Working with Scenarios

Scenarios allow you to model different operational conditions or future
projections:

```python
# Add a scenario
scenario_id = db.add_scenario("High Demand")

# Add property with scenario context
db.add_property(
    ClassEnum.Generator,
    "Generator1",
    "Max Capacity",
    750.0,  # Increased capacity for high demand scenario
    scenario="High Demand"
)

# List all scenarios
scenarios = db.list_scenarios()
print(f"Available scenarios: {scenarios}")
```

## Working with Model Configurations

PlexosDB can be used to build and manage model configuration workflows, not just
object data. In practice, this usually means:

- Defining model/scenario sets for different study cases
- Storing scenario-specific property overrides
- Verifying run-level config flags imported from XML
- Configuring report outputs for post-processing

### 1. Build a model and attach scenarios

```python
from plexosdb.enums import ClassEnum, CollectionEnum

# Add a model and scenarios
db.add_object(ClassEnum.Model, "BaseModel")
db.add_object(ClassEnum.Scenario, "Reference")
db.add_object(ClassEnum.Scenario, "High Demand")

# Link scenarios to the model
db.add_membership(
    parent_class_enum=ClassEnum.Model,
    child_class_enum=ClassEnum.Scenario,
    parent_object_name="BaseModel",
    child_object_name="Reference",
    collection_enum=CollectionEnum.Scenarios,
)
db.add_membership(
    parent_class_enum=ClassEnum.Model,
    child_class_enum=ClassEnum.Scenario,
    parent_object_name="BaseModel",
    child_object_name="High Demand",
    collection_enum=CollectionEnum.Scenarios,
)

print(db.list_scenarios_by_model("BaseModel"))
# ['Reference', 'High Demand']
```

### 2. Add scenario-specific operating assumptions

```python
# Base-case capacity
db.add_property(
    ClassEnum.Generator,
    "Generator1",
    "Max Capacity",
    500.0,
)

# Scenario override for high demand planning case
db.add_property(
    ClassEnum.Generator,
    "Generator1",
    "Max Capacity",
    650.0,
    scenario="High Demand",
)

# Retrieve properties and filter for the scenario value
all_capacity_props = db.get_object_properties(
    ClassEnum.Generator,
    "Generator1",
    property_names="Max Capacity",
)
high_demand_props = [p for p in all_capacity_props if p.get("scenario_name") == "High Demand"]
print(high_demand_props)
```

### 3. Modify simulation configuration classes (Production, Performance, etc.)

Yes, this is supported in PlexosDB through class objects plus attributes. The
common workflow is:

1. Create (or reference) a configuration object in the target class.
2. Discover valid attribute names for that class.
3. Set attribute values with `add_attribute`.
4. Read them back with `get_attribute`.

```python
from plexosdb.enums import ClassEnum

# Example: create configuration objects
db.add_object(ClassEnum.Production, "Production_Config")
db.add_object(ClassEnum.Performance, "Performance_Config")

# Inspect which attributes are valid for each class
production_attrs = db.list_attributes(ClassEnum.Production)
performance_attrs = db.list_attributes(ClassEnum.Performance)
print("Production attributes:", production_attrs)
print("Performance attributes:", performance_attrs)

# Set attribute values (use exact names from list_attributes)
db.add_attribute(
    ClassEnum.Production,
    "Production_Config",
    attribute_name="Unit Commitment Optimality",
    attribute_value=2,
)
db.add_attribute(
    ClassEnum.Performance,
    "Performance_Config",
    attribute_name="MIP Relative Gap",
    attribute_value=0.01,
)

# Read back values
uc_opt_row = db.get_attribute(
    ClassEnum.Production,
    object_name="Production_Config",
    attribute_name="Unit Commitment Optimality",
)
mip_gap_row = db.get_attribute(
    ClassEnum.Performance,
    object_name="Performance_Config",
    attribute_name="MIP Relative Gap",
)
uc_opt = uc_opt_row[0]
mip_gap = mip_gap_row[0]
print("UC optimality:", uc_opt)
print("MIP gap:", mip_gap)
```

You can apply the same pattern to `ClassEnum.PASA`, `ClassEnum.MTSchedule`,
`ClassEnum.STSchedule`, `ClassEnum.Transmission`, and `ClassEnum.Diagnostic`.

For a full Production attributes catalog (defaults, validation, and
descriptions), see
[Production Attributes Reference](api/production_attributes.md).

For a full Performance attributes catalog (defaults, validation, and
descriptions), see
[Performance Attributes Reference](api/performance_attributes.md).

For a full Transmission attributes catalog (defaults, validation, and
descriptions), see
[Transmission Attributes Reference](api/transmission_attributes.md).

For a full PASA attributes catalog (defaults, validation, and descriptions), see
[PASA Attributes Reference](api/pasa_attributes.md).

For a full Diagnostic attributes catalog (defaults, validation, and
descriptions), see
[Diagnostic Attributes Reference](api/diagnostic_attributes.md).

For a full Horizon attributes catalog (defaults, validation, and descriptions),
see [Horizon Attributes Reference](api/horizon_attributes.md).

For a full Model attributes catalog (defaults, validation, and descriptions),
see [Model Attributes Reference](api/model_attributes.md).

### 4. Inspect run configuration flags

When you import from XML, PlexosDB preserves model metadata in `t_config` and
enables `Dynamic` by default (for time series files \*.csv associations).

```python
db = PlexosDB.from_xml("/path/to/your/plexos_model.xml")

config_rows = db.query(
    "SELECT element, value FROM t_config WHERE element IN (?, ?)",
    ("Version", "Dynamic"),
)
config = {element: value for element, value in config_rows}

print(f"PLEXOS version: {config.get('Version')}")
print(f"Dynamic enabled: {config.get('Dynamic')}")
```

Note: `get_config` and `set_config` are currently placeholders in the public
API, so use `query(...)` for now when inspecting `t_config` values directly.

### 5. Configure report outputs

```python
# Add a report object and configure output fields
db.add_object(ClassEnum.Report, "Generator Output Report")
db.add_report(
    object_name="Generator Output Report",
    property="Generation",
    collection=CollectionEnum.Generators,
    parent_class=ClassEnum.System,
    child_class=ClassEnum.Generator,
    phase_id=4,  # Long-term phase
    report_period=True,
    report_summary=True,
)
```

For more report-focused patterns, see
[How to Add Report Configurations](howtos/add_reports.md).

## Working with Collections and Memberships

Collections define relationships between objects in your model:

```python
from plexosdb.enums import CollectionEnum

# Add a region
db.add_object(ClassEnum.Region, "RegionA")

# Create membership: Generator1 belongs to RegionA
db.add_membership(
    parent_class_enum=ClassEnum.Region,
    child_class_enum=ClassEnum.Generator,
    parent_object_name="RegionA",
    child_object_name="Generator1",
    collection_enum=CollectionEnum.Generators
)

# Query memberships
memberships = db.list_object_memberships(ClassEnum.Generator, "Generator1")
for member in memberships:
    print(f"Generator1 belongs to {member['parent_name']} ({member['parent_class_name']})")
```

You can also work with purchaser objects and the corresponding purchasers
collection:

```python
from plexosdb.enums import ClassEnum, CollectionEnum, get_default_collection

# Add a purchaser object
db.add_object(ClassEnum.Purchaser, "RetailerA")

# Confirm default class-to-collection mapping
assert get_default_collection(ClassEnum.Purchaser) == CollectionEnum.Purchasers

# Confirm the System -> Purchaser collection exists in the schema
db.check_collection_exists(
    CollectionEnum.Purchasers,
    parent_class=ClassEnum.System,
    child_class=ClassEnum.Purchaser,
)
```

## Bulk Operations

For large models, PlexosDB provides efficient bulk operations:

```python
# Add multiple objects at once
generator_names = ["Gen1", "Gen2", "Gen3", "Gen4", "Gen5"]
db.add_objects(*generator_names, class_enum=ClassEnum.Generator)

# Bulk property addition using records
property_records = [
    {"name": "Gen1", "Max Capacity": 100.0, "Heat Rate": 9000.0},
    {"name": "Gen2", "Max Capacity": 150.0, "Heat Rate": 9200.0},
    {"name": "Gen3", "Max Capacity": 200.0, "Heat Rate": 8800.0},
]

db.add_properties_from_records(
    property_records,
    object_class=ClassEnum.Generator,
    collection=CollectionEnum.Generators,
    scenario="Base Case"
)
```

## Next Steps

Now that you have completed the tutorial, you can:

1. Explore the [How-to Guides](howtos/index.md) for specific tasks
2. Consult the [API Reference](api/index.md) for detailed method documentation
3. Review examples in the source code test files
