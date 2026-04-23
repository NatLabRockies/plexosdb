---
name: plexosdb
description: |
  Build, inspect, and evolve PLEXOS input databases using plexosdb's
  PlexosDB/SQLiteManager APIs, class/collection navigation, object and
  membership management, property authoring, scenario tagging, and
  XML import/export round-trips.
license: MIT
allowed-tools: Read Edit Grep Glob Bash Write
metadata:
  author: plexosdb
  version: "1.0.0"
  category: power-systems-modeling
---

# plexosdb

## Use when

- Loading an existing PLEXOS XML model into a SQLite-backed `PlexosDB` and
  inspecting its classes, collections, objects, and memberships.
- Creating a new PLEXOS model from scratch (empty schema bootstrap) and
  populating objects, categories, memberships, and properties.
- Authoring or updating object properties, attribute overrides, and
  scenario-tagged values.
- Copying objects (with or without memberships), bulk-inserting property
  records, and cleaning up redundant rows.
- Exporting a PlexosDB session back to PLEXOS XML (`to_xml`) and validating
  round-trip integrity against the original input.
- Writing automation/agent tools (including MCP tools) on top of plexosdb's
  typed enums (`ClassEnum`, `CollectionEnum`) and query helpers.

## Avoid when

- Task has no PLEXOS model or XML schema involvement.
- Task is generic SQL/SQLite tuning without plexosdb domain logic.
- User is asking for PLEXOS solver/runtime behavior instead of input
  authoring.

## Quick start: which doc first?

- Core PlexosDB navigation, add/get/update/delete API contracts:
  [REFERENCE.md](./REFERENCE.md)
- Object memberships and parent/child collection semantics:
  [MEMBERSHIPS.md](./MEMBERSHIPS.md)
- Property authoring (single + bulk), bands, text/tag overrides:
  [PROPERTIES.md](./PROPERTIES.md)
- Scenarios, variable tags, datafile tags, and report tagging:
  [SCENARIOS.md](./SCENARIOS.md)
- XML import/export and schema bootstrap:
  [SERIALIZATION.md](./SERIALIZATION.md)
- How to discover and validate sources:
  [DISCOVERY.md](./DISCOVERY.md)

## Additional Documentation

- [EXAMPLES.md](./EXAMPLES.md), trigger and near-miss prompts.
- [scripts/check_api_symbols.py](./scripts/check_api_symbols.py), optional API
  drift checker for key plexosdb symbols.
- [scripts/inspect_plexos_db.py](./scripts/inspect_plexos_db.py), inspects a
  plexosdb SQLite file: table counts, class/collection rows, and samples.
- [scripts/check_plexos_xml.sh](./scripts/check_plexos_xml.sh), validates a
  PLEXOS XML file is well-formed (via `xmllint`) and has the expected root.

## Workflow

1. Inspect first, change second.
   - Inventory the current database using `list_classes()`,
     `list_collections(class_enum=...)`, `list_objects_by_class(...)`,
     `list_categories(...)`, `list_scenarios()`, `list_models()`.
   - For a specific object, use `get_object_id(...)`,
     `list_object_memberships(...)`, `get_object_properties(...)`, and
     `iterate_properties(...)` to stream full property views.
   - Follow `DISCOVERY.md` to find canonical sources and confirm exact API
     behavior (plexosdb source is the source of truth).

2. Define boundaries before mutating.
   - Keep domain intent typed: use `ClassEnum` and `CollectionEnum` instead
     of raw strings whenever possible.
   - Decide up-front whether data belongs as a property (time-varying,
     scenario-tagged, banded) vs an attribute (static metadata).
   - For parent/child wiring, prefer `add_membership(...)` and
     `copy_object_memberships(...)` over hand-crafting SQL.

3. Apply minimal schema changes.
   - Add objects with `add_object(...)` / `add_objects(...)` with explicit
     category when organization matters.
   - Add properties with `add_property(...)` for single values or
     `add_properties_from_records(...)` for bulk inserts (see
     [PROPERTIES.md](./PROPERTIES.md) for record shape).
   - Use `copy_object(copy_properties=True, copy_memberships=True)` to
     clone entire modeled objects.

4. Verify persistence behavior.
   - Validate that `to_xml(path)` round-trips by re-importing with
     `PlexosDB.from_xml(path)` and diffing object/property counts.
   - Use [scripts/check_plexos_xml.sh](./scripts/check_plexos_xml.sh) to
     catch malformed XML before import.
   - Use [scripts/inspect_plexos_db.py](./scripts/inspect_plexos_db.py) when
     debugging SQLite state directly.

5. Respect extension hooks and integrated references.
   - For scenario-aware property workflows and variable/datafile tags, use
     [SCENARIOS.md](./SCENARIOS.md).
   - For cross-cutting relationships (generator-to-node, region-to-zone,
     etc.) use [MEMBERSHIPS.md](./MEMBERSHIPS.md).
   - For import/export and schema bootstrap flows, use
     [SERIALIZATION.md](./SERIALIZATION.md).

## Output

- Database inspection findings (what exists today: classes, counts, objects).
- Proposed model changes with explicit `ClassEnum`/`CollectionEnum` usage.
- Exact PlexosDB APIs called for navigation, mutation, and verification.
- XML round-trip and/or SQLite inspection checks performed.
- Membership integrity notes (including whether parent/child wiring needed
  `copy_object_memberships` or manual `add_membership` fix-ups).
- Integrated references consulted and why.
