# Checks

Validation helpers for checking classes, objects, collections, memberships,
properties, attributes, scenarios, data records, and tags in a `PlexosDB`
database.

For whole-database validation and text reports, see
[Validating a Database](../howtos/validate_database.md). Use the public
`PlexosDB.validate_database()` entry point; `_find_*` functions are internal
helpers that consume a `SQLiteManager`.

```{eval-rst}
.. automodule:: plexosdb.checks
    :members:
    :undoc-members:
    :show-inheritance:
```

The existence-check helpers accept a `PlexosDB` instance as their first
argument. The same checks are also available as convenience methods on
`PlexosDB` where the class exposes them.
