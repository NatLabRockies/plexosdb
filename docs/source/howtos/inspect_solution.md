# Inspecting a PLEXOS Solution

This guide shows how to import a PLEXOS solution ZIP file into SQLite and
inspect its table catalog using the `show_db_tables` helper.

## Converting a solution

Use `PlexosSolution` to import the ZIP into SQLite. Pass
`decode_bin_values=False` to skip writing BIN payload data — the table catalog
only needs the XML metadata tables and is then fast even for large solutions:

```python
from plexosdb import PlexosSolution, show_db_tables

sol = PlexosSolution.from_zip("my_solution.zip")
sol.to_sqlite("output.sqlite", if_exists="replace", decode_bin_values=False)
```

## Printing the table catalog

Call `show_db_tables` directly on the `PlexosSolution` instance after
`to_sqlite()` has been called:

```python
show_db_tables(sol)
```

### Example output

```text
┌───────────────────────────┬──────────────┬──────────────────────────────────────────────────────────┬────────────┬──────────────────────────────┬──────────────────────┬───────────────────────────┬──────────────────────────┬────────────────────────┬────────────────────┬──────────┬───────────────┬───────────────┐
│       table_catalog       │ table_schema │                        table_name                        │ table_type │ self_referencing_column_name │ reference_generation │ user_defined_type_catalog │ user_defined_type_schema │ user_defined_type_name │ is_insertable_into │ is_typed │ commit_action │ TABLE_COMMENT │
│          varchar          │   varchar    │                         varchar                          │  varchar   │           varchar            │       varchar        │          varchar          │         varchar          │        varchar         │      varchar       │ varchar  │    varchar    │    varchar    │
├───────────────────────────┼──────────────┼──────────────────────────────────────────────────────────┼────────────┼──────────────────────────────┼──────────────────────┼───────────────────────────┼──────────────────────────┼────────────────────────┼────────────────────┼──────────┼───────────────┼───────────────┤
│ Model model_2012 Solution │ data         │ ST__Interval__Batteries__Generation                      │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ data         │ ST__Interval__Batteries__Generation_Capacity             │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ data         │ ST__Interval__Batteries__Installed_Capacity              │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ data         │ ST__Interval__Batteries__Load                            │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ data         │ ST__Interval__Batteries__SoC                             │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ data         │ ST__Interval__Generators__Available_Capacity             │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ data         │ ST__Interval__Generators__Average_Heat_Rate              │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ data         │ ST__Interval__Generators__Capacity_Curtailed             │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ data         │ ST__Interval__Generators__Capacity_Factor                │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ data         │ ST__Interval__Generators__Emissions_Cost                 │ BASE TABLE │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ YES                │ NO       │ NULL          │ NULL          │
│             ·             │      ·       │                            ·                             │     ·      │              ·               │          ·           │             ·             │            ·             │           ·            │         ·          │    ·     │       ·       │       ·       │
│             ·             │      ·       │                            ·                             │     ·      │              ·               │          ·           │             ·             │            ·             │           ·            │         ·          │    ·     │       ·       │       ·       │
│             ·             │      ·       │                            ·                             │     ·      │              ·               │          ·           │             ·             │            ·             │           ·            │         ·          │    ·     │       ·       │       ·       │
│ Model model_2012 Solution │ report       │ ST__Year__Reserves__Price                                │ VIEW       │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ NO                 │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ report       │ ST__Year__Reserves__Provision                            │ VIEW       │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ NO                 │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ report       │ ST__Year__Reserves__Shortage                             │ VIEW       │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ NO                 │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ report       │ ST__Year__Storages__Generation                           │ VIEW       │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ NO                 │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ report       │ ST__Year__Storages__Inflow                               │ VIEW       │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ NO                 │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ report       │ ST__Year__Storages__Initial_Volume                       │ VIEW       │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ NO                 │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ report       │ ST__Year__Storages__Max_Volume                           │ VIEW       │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ NO                 │ NO       │ NULL          │ NULL          │
│ Model model_2012 Solution │ report       │ ST__Year__Storages__Pump_Load                            │ VIEW       │ NULL                         │ NULL                 │ NULL                      │ NULL                     │ NULL                   │ NO                 │ NO       │ NULL          │ NULL          │
└───────────────────────────┴──────────────┴──────────────────────────────────────────────────────────┴────────────┴──────────────────────────────┴────────────┴───────────────────────────┴──────────────────────────┴────────────────────────┴────────────────────┴──────────┴───────────────┴───────────────┘
  267 rows (20 shown)  13 columns
```

Rows that do not fit within `max_rows` are replaced by three `·` rows. The
default limit is 20; pass a different value to show more:

```python
with client as db:
    show_db_tables(db, max_rows=50)
```

## Columns

| Column               | Description                                                                 |
| -------------------- | --------------------------------------------------------------------------- |
| `table_catalog`      | Stem of the source ZIP file (used as the catalog name).                     |
| `table_schema`       | SQLite schema name: `main`, `data`, `report`, or any other attached schema. |
| `table_name`         | Name of the table or view.                                                  |
| `table_type`         | `BASE TABLE` for tables; `VIEW` for views.                                  |
| `is_insertable_into` | `YES` for writable tables, `NO` for views.                                  |
| `is_typed`           | Always `NO`.                                                                |
| remaining columns    | `NULL` — present for compatibility with `information_schema.tables`.        |

## Schema meanings

- **`main`** — raw tables imported directly from the PLEXOS solution XML (e.g.
  `t_class`, `t_object`, `t_membership`).
- **`data`** — derived result tables that can be materialized from BIN files
  (e.g. `ST__Interval__Generators__Generation`).
- **`report`** — same derived tables exposed as views with enriched metadata
  joins.
