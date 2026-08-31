# SQLite Solution Reader

The SQLite solution reader imports a PLEXOS solution ZIP into SQLite and
materializes derived result tables for analysis. Import it explicitly to
distinguish it from the DuckDB-backed solution wrapper:

```python
from plexosdb.solution_reader import PlexosSolution
```

```{eval-rst}
.. automodule:: plexosdb.solution_reader.solution
    :members:
    :undoc-members:
    :show-inheritance:
```

## Display Helpers

```{eval-rst}
.. automodule:: plexosdb.solution_reader.display
    :members:
    :undoc-members:
    :show-inheritance:
```

## Result Types

```{eval-rst}
.. automodule:: plexosdb.solution_reader.types
    :members:
    :undoc-members:
    :show-inheritance:
```

See [Inspecting a PLEXOS Solution](../howtos/inspect_solution.md) for a
complete ZIP-to-SQLite workflow.
