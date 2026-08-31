# DuckDB Solution Reader

The DuckDB solution reader converts a PLEXOS solution ZIP with `plexos2duckdb`
and exposes lazy DuckDB relations for analysis. Import it explicitly to
distinguish it from the SQLite-backed solution reader:

```python
from plexosdb.db_solution import PlexosSolution
```

```{eval-rst}
.. automodule:: plexosdb.db_solution
    :members:
    :undoc-members:
    :show-inheritance:
```

## Result Types

```{eval-rst}
.. automodule:: plexosdb.db_solution_models
    :members:
    :undoc-members:
    :show-inheritance:
```

See [Reading a PLEXOS Solution](../howtos/read_solution.md) for a complete
ZIP-to-DuckDB workflow.
