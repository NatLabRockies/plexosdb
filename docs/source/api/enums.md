# Enumerations

## Version Coverage

The enum module now includes coverage constants for schema sizes in supported
versions:

- v9.2: 96 classes, 776 collections
- v10: 96 classes, 806 collections

## v10 Collection Differences vs v9.2

The following 30 collection relationships are present in v10 and not present in
v9.2.

| Collection Relationship                            |
| -------------------------------------------------- |
| Capacity Facilities: Zone -> Facility              |
| Capacity Gas Plants: Zone -> Gas Plant             |
| Capacity Gas Storages: Zone -> Gas Storage         |
| Capacity Heat Plants: Zone -> Heat Plant           |
| Capacity Water Plants: Zone -> Water Plant         |
| Conditions: Battery -> Variable                    |
| Entities: Flow Node -> Entity                      |
| Entities: Flow Path -> Entity                      |
| Entities: Flow Storage -> Entity                   |
| Facilities: Region -> Facility                     |
| Facilities: Zone -> Facility                       |
| Gas Paths: Gas Contract -> Gas Path                |
| Gas Paths: Gas Pipeline -> Gas Path                |
| Gas Plants: Region -> Gas Plant                    |
| Gas Plants: Zone -> Gas Plant                      |
| Gas Storages: Region -> Gas Storage                |
| Gas Storages: Zone -> Gas Storage                  |
| Heat Plants: Region -> Heat Plant                  |
| Heat Plants: Zone -> Heat Plant                    |
| Initial Gas Path: Gas Transport -> Gas Path        |
| Interfaces Monitored: Contingency -> Interface     |
| Lines: Reserve -> Line                             |
| Lines Monitored: Contingency -> Line               |
| Node: Gas Storage -> Node                          |
| ORDC System Lambda Nodes: Pool -> Node             |
| Start Gas Nodes: Generator -> Gas Node             |
| Transformers Monitored: Contingency -> Transformer |
| Water Plants: Region -> Water Plant                |
| Water Plants: Zone -> Water Plant                  |
| Zones: Reserve -> Zone                             |

```{eval-rst}
.. automodule:: plexosdb.enums
    :members:
    :undoc-members:
    :show-inheritance:
```
