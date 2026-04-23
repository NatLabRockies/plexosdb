# plexosdb Skill Trigger Examples

Use these prompts to validate when this skill should activate.

## Should trigger

1. "Load `model.xml` with plexosdb and list every generator together
   with its `Max Capacity` property."
2. "I have a PLEXOS XML. Rename all generators in category `Thermal`
   and re-export to `model_v2.xml`."
3. "Bulk-insert 10,000 property rows for generators using
   `add_properties_from_records` and verify round-trip with
   `from_xml`/`to_xml`."
4. "Create a scenario `Low_Demand`, attach scaled `Max Capacity`
   overrides for a subset of generators, and wire the scenario into
   the `BaseModel` model."
5. "Copy object `GEN01` into `GEN02` including memberships and
   properties, then diff the two objects' property tables."
6. "Bootstrap an empty PLEXOS model with `create_schema()`, add two
   regions, two nodes, and wire generators to nodes."
7. "Diagnose why `add_property` silently drops rows — probably missing
   memberships; use `list_object_memberships` to confirm."

## Near-miss (should NOT trigger)

1. "My task is generic SQLite performance tuning with no PLEXOS
   involvement."
2. "Help me integrate infrasys `System` components with a web UI."
   → use the `infrasys` skill instead.
3. "Summarize PLEXOS solver behavior during UC runs."
   → out of scope for plexosdb's input-database domain.
4. "Generic XML schema advice with no PLEXOS data model."

## Borderline prompts (trigger + integrated reference)

1. "Round-trip my XML and make sure scenario-tagged property
   overrides survive."
   - Trigger this skill, then use `SERIALIZATION.md` and
     `SCENARIOS.md`.
2. "Build an MCP tool that attaches datafile tags to region load
   properties."
   - Trigger this skill, then use `PROPERTIES.md` and `SCENARIOS.md`.
3. "Replicate every membership of `GEN01` onto a new `GEN01_copy`
   object without cloning properties."
   - Trigger this skill, then use `MEMBERSHIPS.md`.
