# Gas Library: Systems and Memberships

This guide shows how to create Gas Library objects and memberships using
`ClassEnum` and `CollectionEnum`.

```{note}
Most examples in the current docs are Electric Library oriented.
Use this page as the Gas Library counterpart for object and membership setup.
```

## Discover Valid Gas Collections First

Start from an existing Gas XML and inspect available parent-child collection
combinations.

```python
from plexosdb import PlexosDB
from plexosdb.enums import ClassEnum

db = PlexosDB.from_xml("/path/to/gas_sys.xml")
print(db.list_collections(parent_class=ClassEnum.GasNode))
```

Example result for `ClassEnum.GasNode`:

```text
[
  {'collection_id': 427, 'collection_name': 'Template', 'parent_class_name': 'Gas Node', 'child_class_name': 'Gas Node'},
  {'collection_id': 429, 'collection_name': 'Gas Zones', 'parent_class_name': 'Gas Node', 'child_class_name': 'Gas Zone'},
  {'collection_id': 431, 'collection_name': 'Gas Paths', 'parent_class_name': 'Gas Node', 'child_class_name': 'Gas Path'},
  {'collection_id': 432, 'collection_name': 'Facilities', 'parent_class_name': 'Gas Node', 'child_class_name': 'Facility'},
  {'collection_id': 433, 'collection_name': 'Markets', 'parent_class_name': 'Gas Node', 'child_class_name': 'Market'},
  {'collection_id': 434, 'collection_name': 'Constraints', 'parent_class_name': 'Gas Node', 'child_class_name': 'Constraint'},
  {'collection_id': 435, 'collection_name': 'Objectives', 'parent_class_name': 'Gas Node', 'child_class_name': 'Objective'},
  {'collection_id': 430, 'collection_name': 'Gas Transports', 'parent_class_name': 'Gas Node', 'child_class_name': 'Gas Transport'}
]
```

Use this output to choose valid memberships for your model.

## Create Core Gas Objects

```python
from plexosdb import PlexosDB
from plexosdb.enums import ClassEnum

# Reuse a Gas XML-backed database so Gas classes/collections exist.
db = PlexosDB.from_xml("/path/to/gas_sys.xml")

# Core gas objects
db.add_object(ClassEnum.GasNode, "GN_x")
db.add_object(ClassEnum.GasZone, "GZ_x")
db.add_object(ClassEnum.GasPath, "GP_x")
db.add_object(ClassEnum.GasTransport, "GT_x")

# Related classes frequently used with Gas Node
db.add_object(ClassEnum.Facility, "FAC_x")
db.add_object(ClassEnum.Market, "MKT_x")
```

## Create Extended Heat + Gas Objects

Use this block when you want a broader sandbox that includes the full Heat/Gas
set below:

- `HeatPlant`, `HeatNode`, `HeatStorage`
- `GasField`, `GasPlant`, `GasPipeline`, `GasNode`, `GasStorage`
- `GasDemand`, `GasDSMProgram`, `GasBasin`, `GasZone`
- `GasContract`, `GasTransport`, `GasPath`, `GasCapacityReleaseOffer`

```python
from plexosdb.enums import ClassEnum

db = PlexosDB.from_xml("/path/to/gas_sys.xml")

objects_to_create = [
    (ClassEnum.HeatPlant, "HP_1"),
    (ClassEnum.HeatNode, "HN_1"),
    (ClassEnum.HeatStorage, "HS_1"),
    (ClassEnum.GasField, "GF_1"),
    (ClassEnum.GasPlant, "GPL_1"),
    (ClassEnum.GasPipeline, "GPI_1"),
    (ClassEnum.GasNode, "GN_1"),
    (ClassEnum.GasStorage, "GS_1"),
    (ClassEnum.GasDemand, "GD_1"),
    (ClassEnum.GasDSMProgram, "GDSM_1"),
    (ClassEnum.GasBasin, "GB_1"),
    (ClassEnum.GasZone, "GZ_1"),
    (ClassEnum.GasContract, "GC_1"),
    (ClassEnum.GasTransport, "GT_1"),
    (ClassEnum.GasPath, "GPA_1"),
    (ClassEnum.GasCapacityReleaseOffer, "GCRO_1"),
]

for class_enum, object_name in objects_to_create:
    if not db.check_object_exists(class_enum, object_name):
        db.add_object(class_enum, object_name)
```

## Create Heat/Gas Memberships for a Full Chain

```python
from plexosdb.enums import CollectionEnum

# Verify valid collections for each parent class before adding links.
print(db.list_collections(parent_class=ClassEnum.GasField))
print(db.list_collections(parent_class=ClassEnum.GasContract))
print(db.list_collections(parent_class=ClassEnum.GasTransport))
print(db.list_collections(parent_class=ClassEnum.GasDemand))

# Gas Field -> Gas Basin
db.add_membership(
    parent_class_enum=ClassEnum.GasField,
    child_class_enum=ClassEnum.GasBasin,
    parent_object_name="GF_1",
    child_object_name="GB_1",
    collection_enum=CollectionEnum.GasBasins,
)

# Gas Field -> Gas Node
db.add_membership(
    parent_class_enum=ClassEnum.GasField,
    child_class_enum=ClassEnum.GasNode,
    parent_object_name="GF_1",
    child_object_name="GN_1",
    collection_enum=CollectionEnum.GasNodes,
)

# Gas Contract -> Gas Field
db.add_membership(
    parent_class_enum=ClassEnum.GasContract,
    child_class_enum=ClassEnum.GasField,
    parent_object_name="GC_1",
    child_object_name="GF_1",
    collection_enum=CollectionEnum.GasFields,
)

# Gas Contract -> Gas Transport
db.add_membership(
    parent_class_enum=ClassEnum.GasContract,
    child_class_enum=ClassEnum.GasTransport,
    parent_object_name="GC_1",
    child_object_name="GT_1",
    collection_enum=CollectionEnum.GasTransports,
)

# Gas Transport -> Gas Path
db.add_membership(
    parent_class_enum=ClassEnum.GasTransport,
    child_class_enum=ClassEnum.GasPath,
    parent_object_name="GT_1",
    child_object_name="GPA_1",
    collection_enum=CollectionEnum.GasPaths,
)

# Gas Demand -> Gas Node
db.add_membership(
    parent_class_enum=ClassEnum.GasDemand,
    child_class_enum=ClassEnum.GasNode,
    parent_object_name="GD_1",
    child_object_name="GN_1",
    collection_enum=CollectionEnum.GasNodes,
)
```

## Create Model/Scenario Variants (System Alternatives)

In PLEXOS there is one `System` object. To represent different "systems" for
study purposes, create separate `Model` and `Scenario` objects and link them.

```python
from plexosdb.enums import ClassEnum, CollectionEnum

# Model variants (system alternatives)
db.add_object(ClassEnum.Model, "GasSystem_Base")
db.add_object(ClassEnum.Model, "GasSystem_Expansion")

# Scenario variants
db.add_object(ClassEnum.Scenario, "Base")
db.add_object(ClassEnum.Scenario, "HighDemand")
db.add_object(ClassEnum.Scenario, "LowSupply")

# Link each model to scenarios
db.add_membership(
    parent_class_enum=ClassEnum.Model,
    child_class_enum=ClassEnum.Scenario,
    parent_object_name="GasSystem_Base",
    child_object_name="Base",
    collection_enum=CollectionEnum.Scenarios,
)

db.add_membership(
    parent_class_enum=ClassEnum.Model,
    child_class_enum=ClassEnum.Scenario,
    parent_object_name="GasSystem_Expansion",
    child_object_name="HighDemand",
    collection_enum=CollectionEnum.Scenarios,
)

db.add_membership(
    parent_class_enum=ClassEnum.Model,
    child_class_enum=ClassEnum.Scenario,
    parent_object_name="GasSystem_Expansion",
    child_object_name="LowSupply",
    collection_enum=CollectionEnum.Scenarios,
)
```

## Create Gas Memberships with `CollectionEnum`

```python
from plexosdb.enums import CollectionEnum

# Note:
# db.add_object(...) already creates the default System -> object membership.

# Gas Node -> Gas Zone
db.add_membership(
    parent_class_enum=ClassEnum.GasNode,
    child_class_enum=ClassEnum.GasZone,
    parent_object_name="GN_x",
    child_object_name="GZ_x",
    collection_enum=CollectionEnum.GasZones,
)

# Gas Node -> Gas Path
db.add_membership(
    parent_class_enum=ClassEnum.GasNode,
    child_class_enum=ClassEnum.GasPath,
    parent_object_name="GN_x",
    child_object_name="GP_x",
    collection_enum=CollectionEnum.GasPaths,
)

# Gas Node -> Gas Transport
db.add_membership(
    parent_class_enum=ClassEnum.GasNode,
    child_class_enum=ClassEnum.GasTransport,
    parent_object_name="GN_x",
    child_object_name="GT_x",
    collection_enum=CollectionEnum.GasTransports,
)

# Gas Node -> Facility
db.add_membership(
    parent_class_enum=ClassEnum.GasNode,
    child_class_enum=ClassEnum.Facility,
    parent_object_name="GN_x",
    child_object_name="FAC_x",
    collection_enum=CollectionEnum.Facilities,
)

# Gas Node -> Market
db.add_membership(
    parent_class_enum=ClassEnum.GasNode,
    child_class_enum=ClassEnum.Market,
    parent_object_name="GN_x",
    child_object_name="MKT_x",
    collection_enum=CollectionEnum.Markets,
)
```

## Mapping Display Names to Enums

`db.list_collections()` returns collection names as display text (for example,
`"Gas Zones"`). For API calls, use `CollectionEnum` values (for example,
`CollectionEnum.GasZones`).

If you need to parse display text dynamically, use `parse_collection_enum`:

```python
from plexosdb.enums import parse_collection_enum

collection_enum = parse_collection_enum("Gas Zones")
assert collection_enum == CollectionEnum.GasZones
```
