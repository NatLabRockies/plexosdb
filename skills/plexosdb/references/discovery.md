# plexosdb Reference Discovery Protocol

This guide defines how the `plexosdb` skill should find additional reference
docs quickly and reliably.

## Goal

When a task references unfamiliar APIs or behavior, the skill should follow a
deterministic discovery sequence instead of ad-hoc searching.

## Recommended read order

1. `SKILL.md`
2. `reference.md`
3. `memberships.md` (if parent/child wiring is involved)
4. `properties.md` (if property authoring/updating is involved)
5. `scenarios.md` (if scenario/variable/datafile tags are involved)
6. `serialization.md` (if XML import/export or schema bootstrap is involved)
7. `../evals/trigger-prompts.json` (trigger and near-miss sanity checks)
8. Shell sanity checks (`../scripts/*.sh`) when XML validation or
   reproducibility is needed

## Canonical external sources

Prefer these in order:

1. Installed package metadata
   - `plexosdb` on PyPI: <https://pypi.org/project/plexosdb/>
2. Repository documentation
   - `README.md` at the repo root
   - `docs/source/index.md`, `docs/source/tutorial.md`
   - `docs/source/howtos/*.md`
3. Installed package source code (source of truth for APIs)
   - `plexosdb.db` (`PlexosDB` class with all `add_*`, `get_*`, `list_*`,
     `check_*`, `update_*`, `delete_*` methods)
   - `plexosdb.db_manager` (`SQLiteManager`)
   - `plexosdb.enums` (`ClassEnum`, `CollectionEnum`)
   - `plexosdb.xml_handler` (`XMLHandler` — XML → SQLite loader)
   - `plexosdb.schema.sql` (SQL schema DDL)
   - `plexosdb.queries/` (packaged SQL queries)

Example (prints module file paths):

```bash
uv run --with plexosdb python - <<'PY'
import plexosdb.db as db
import plexosdb.db_manager as dm
import plexosdb.enums as en
import plexosdb.xml_handler as xh
print(db.__file__)
print(dm.__file__)
print(en.__file__)
print(xh.__file__)
PY
```

If docs and source disagree, trust source signatures/behavior and note the
mismatch.

## Discovery workflow

1. Extract task keywords and symbol candidates.
   - Example: `add_property`, `add_memberships_from_records`,
     `list_valid_properties`, `to_xml`, `from_xml`.
2. Find candidate files.
   - Start from `reference.md`, then targeted file search in `src/plexosdb/` for
     `def <name>`.
3. Confirm symbol behavior with source.
   - Check signatures and docstrings in `db.py` / `db_manager.py`.
4. Cross-check related docs.
   - Pull the matching how-to under `docs/source/howtos/`.
5. Record provenance in output.
   - State which files were consulted and which one was decisive.

## Practical search strategy

- Prefer narrow, literal symbol searches before broad fuzzy search.
- Search for method definitions (`def <name>`) when API exactness matters.
- Use docs for intent and examples, source for final truth.
- Use source-level symbol checks (`src/plexosdb/db.py`, `checks.py`, and related
  tests) for API drift; do not rely on bundled Python helper scripts.
- Use `../scripts/check_plexos_xml.sh` for fast malformed-XML checks
  (`xmllint --noout`).
- Debug SQLite state through plexosdb APIs first; avoid bundled scripts that
  inspect or mutate database internals directly.

## Escalation rules

Stay within this skill and choose the right integrated reference by task
center-of-gravity:

- `memberships.md` for parent/child wiring and collection semantics.
- `properties.md` for single and bulk property authoring, bands, text overrides.
- `scenarios.md` for scenario/variable/datafile override mechanics and
  model-to-scenario attachment.
- `serialization.md` for XML import/export, schema bootstrap, and round-trip
  verification.

## Output checklist (for the skill)

- APIs confirmed (exact method names and `ClassEnum`/`CollectionEnum` values
  used).
- Docs/source consulted (paths).
- Any docs vs source mismatches found.
- Chosen boundary between integrated references inside this skill.
