# plexosdb Serialization and Schema Bootstrap Reference

Use this document for PLEXOS XML import/export, empty-model schema bootstrap,
and SQLite persistence workflows in plexosdb.

## Scope in this skill

This reference covers:

- `PlexosDB.from_xml(...)` and `PlexosDB.to_xml(...)`
- empty-model bootstrap via `PlexosDB()` + `create_schema(seed_defaults=True)`
- in-process SQLite persistence via `SQLiteManager`
- round-trip validation checks
- PLEXOS version inspection (`get_plexos_version`)

## Which persistence path to use

Use `from_xml` / `to_xml` when the canonical artifact is a PLEXOS XML file that
PLEXOS Desktop or third-party tooling needs to read or write:

```python
from plexosdb import PlexosDB

db = PlexosDB.from_xml("model.xml")
# ... mutate ...
db.to_xml("model_out.xml")
```

Use an empty in-memory database when building a model from scratch (for example,
from CSV or agent-driven authoring):

```python
db = PlexosDB()
db.create_schema(seed_defaults=True)
# ... add classes/objects/memberships/properties ...
db.to_xml("generated.xml")
```

Quick rule:

- External PLEXOS-consumable artifact → `to_xml(...)`.
- Agent-local intermediate state → SQLite in-memory + `to_xml` at the end.

## On-disk layout

`to_xml("path/model.xml")` writes a single XML file that follows the PLEXOS
`MasterDataSet` root element. There is no sibling directory (unlike infrasys
time-series archives).

The SQLite projection is held by the private `PlexosDB._db` (a `SQLiteManager`);
there is no public accessor, and `backup_database` is not implemented in current
plexosdb. To cache an expensive `from_xml(...)` load, materialize to a file path
at construction instead:

```python
# Load once, persisted to a SQLite file
db = PlexosDB.from_xml("model.xml", fpath_or_conn="model_state.sqlite")

# Reopen the cached SQLite file later without re-parsing the XML
cached = PlexosDB(fpath_or_conn="model_state.sqlite")
```

## Empty-model bootstrap

`create_schema(seed_defaults=True)` runs the packaged `schema.sql` and seeds the
default rows, which sets up:

- the base class table populated from `ClassEnum`
- the base collection table populated from `CollectionEnum`
- the `System` object (parent of most top-level memberships)
- default categories and configuration rows
- empty property/attribute tables

`seed_defaults=True` is required before `add_object(...)` works on a fresh
database, and it seeds only the System->child (default) collections. Cross-class
wiring and named-property catalogs come from a model loaded via `from_xml(...)`.

After bootstrap, a minimum viable model needs at least:

1. At least one class-specific object (e.g., a `Generator`).
2. A `Model` object so PLEXOS has something to run.

`add_object(...)` creates the object's `System` membership automatically, so
there is no separate System-wiring step (a duplicate raises).

```python
db = PlexosDB()
db.create_schema(seed_defaults=True)

# add_object also creates the System -> Generator membership.
db.add_object(ClassEnum.Generator, "GEN01")
db.add_object(ClassEnum.Model, "BaseModel")
```

## Round-trip validation checklist

After any non-trivial change:

1. Export: `db.to_xml("tmp.xml")`.
2. Re-import: `reloaded = PlexosDB.from_xml("tmp.xml")`.
3. Validate counts per class:
   ```python
   for cls in ClassEnum:
       before = db.list_objects_by_class(cls)
       after = reloaded.list_objects_by_class(cls)
       assert sorted(before) == sorted(after), cls
   ```
4. Validate property counts for touched objects:
   ```python
   before = db.get_object_properties(ClassEnum.Generator, "GEN01")
   after = reloaded.get_object_properties(
       ClassEnum.Generator, "GEN01"
   )
   assert len(before) == len(after)
   ```
5. Validate that scenarios and models survived:
   ```python
   assert sorted(db.list_scenarios()) == sorted(
       reloaded.list_scenarios()
   )
   assert sorted(db.list_models()) == sorted(reloaded.list_models())
   ```

## Inspecting PLEXOS version

PLEXOS XML files carry a version string. Use:

```python
version = db.get_plexos_version()  # tuple[int, ...] | None
```

Version drift often explains "file imports but property names are unknown"
issues — PLEXOS regularly adds or renames collection properties.

## Storage behavior

- `PlexosDB()` uses an in-memory SQLite database by default.
- `PlexosDB.from_xml(xml_path, db_path=...)` can materialize the imported
  database to a disk file.
- `to_xml(...)` is read-only with respect to the live database (it reads from
  SQLite and writes the XML serializer output).

## Common failure modes

- Invalid XML (truncated file, wrong encoding, not PLEXOS format): catch early
  with `bash scripts/check_plexos_xml.sh <path>`.
- Unknown class or collection during import — typically means the XML was
  produced by a newer PLEXOS than the `ClassEnum`/`CollectionEnum` values known
  to plexosdb; confirm against `src/plexosdb/db.py`, `checks.py`, and related
  tests, then upgrade plexosdb if needed.
- Round-trip produces extra rows: usually caused by mutating after export but
  re-reading from the original path; always diff against a freshly exported
  copy.
- `create_schema(...)` raises on an already-initialized database: call it only
  on a fresh `PlexosDB()` instance.
- `add_object(...)` raises `AssertionError` on a schema created without
  `seed_defaults=True`, because the default collection it needs is missing.

## Operational validation utilities

Validate XML well-formedness and root element:

```bash
bash scripts/check_plexos_xml.sh path/to/model.xml --root MasterDataSet
```

Inspect the projected model through plexosdb APIs first:

```python
from plexosdb import ClassEnum, PlexosDB

db = PlexosDB(fpath_or_conn="path/to/model.sqlite")
print(db.list_objects_by_class(ClassEnum.Generator))
```

Inspect installed source paths (source of truth for API signatures):

```bash
uv run --with plexosdb python - <<'PY'
import plexosdb.db as db
import plexosdb.db_manager as dm
import plexosdb.xml_handler as xh
import plexosdb.enums as en
print(db.__file__)
print(dm.__file__)
print(xh.__file__)
print(en.__file__)
PY
```

## Related references

- [reference.md](./reference.md) for the core navigation/mutation APIs.
- [memberships.md](./memberships.md) for the wiring that a new model must
  include before `to_xml`.
- [properties.md](./properties.md) for the property rows that survive a
  round-trip.
