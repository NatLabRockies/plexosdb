# Inspecting a PLEXOS Solution with SQLite

This guide shows how to import a PLEXOS solution ZIP file into SQLite and
inspect its table catalog using the `show_db_tables` helper.

This guide uses the SQLite-backed `PlexosSolution` imported from
`plexosdb.solution_reader`. It is separate from the DuckDB-backed class in
`plexosdb.db_solution`. See the
[SQLite solution API reference](../api/solution_reader.md) for the complete API.

## Converting a solution

Use `PlexosSolution` to import the ZIP into SQLite. Pass
`decode_bin_values=False` to skip writing BIN payload data — the table catalog
only needs the XML metadata tables and is then fast even for large solutions:

```python
from plexosdb.solution_reader import PlexosSolution, show_db_tables

sol = PlexosSolution.from_zip("my_solution.zip")
sol.to_sqlite("output.sqlite", if_exists="replace", decode_bin_values=False)
```

:::{note} `decode_bin_values=False` is only appropriate for catalog inspection.
If you later call `materialize_table()` on the same instance, BIN decoding will
be triggered automatically. If you open the database with `from_sqlite()` and
BIN data was never decoded, you will get a `RuntimeError` asking you to
re-import from the ZIP with `decode_bin_values=True`. :::

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
with sol as db:
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

## Reading data from the result tables

### Understanding the table name

Every derived table name encodes four pieces of information separated by `__`:

```
{Phase}__{Period}__{Collection}__{Property}
```

| Segment      | Example values                             | Meaning                       |
| ------------ | ------------------------------------------ | ----------------------------- |
| `Phase`      | `ST`, `MT`, `LT`, `PASA`                   | PLEXOS simulation phase       |
| `Period`     | `Interval`, `Day`, `Week`, `Month`, `Year` | Time resolution of the result |
| `Collection` | `Generators`, `Batteries`, `Regions`       | PLEXOS object collection      |
| `Property`   | `Generation`, `Load`, `Price`              | Reported property name        |

For example, `ST__Interval__Generators__Generation` holds interval-level
generator generation values from the ST (Short-Term) phase.

### Columns in a report table

The `report` and `data` schemas expose slightly different columns.

**`report` schema** (use this for analysis):

| Column            | Type    | Description                                                                                                              |
| ----------------- | ------- | ------------------------------------------------------------------------------------------------------------------------ |
| `band`            | INTEGER | Band number (1 for single-band properties).                                                                              |
| `sample_name`     | TEXT    | Stochastic sample label; `'Mean'` for deterministic runs.                                                                |
| `name`            | TEXT    | Object name (e.g. generator or region name).                                                                             |
| `category`        | TEXT    | Object category.                                                                                                         |
| `timestamp`       | TEXT    | Datetime string matching the period resolution.                                                                          |
| `interval_length` | REAL    | Duration of the period in hours (NULL for non-interval data).                                                            |
| `{Property}`      | REAL    | Numeric result value — **named after the property** (last segment of the table name, e.g. `Generation` or `Build_Cost`). |
| `unit`            | TEXT    | Unit string (e.g. `'MW'`, `'MWh'`).                                                                                      |

**`data` schema** (raw materialized):

| Column        | Type    | Description                                |
| ------------- | ------- | ------------------------------------------ |
| `name`        | TEXT    | Object name.                               |
| `sample_name` | TEXT    | Stochastic sample label.                   |
| `band_id`     | INTEGER | Band number.                               |
| `block_id`    | INTEGER | Internal period block identifier.          |
| `datetime`    | TEXT    | Raw datetime string from the period table. |
| `value`       | REAL    | Numeric result value.                      |

### Querying with the built-in connection

`PlexosSolution.connection` is a standard `sqlite3.Connection`. You can query
report tables directly after materializing them.

In the `report` schema the value column is **named after the property** (last
segment of the table name). Extract it from the table name:

```python
from plexosdb.solution_reader import PlexosSolution

sol = PlexosSolution.from_zip("my_solution.zip")
sol.to_sqlite("output.sqlite", if_exists="replace")

table = "ST__Interval__Generators__Generation"\
# splits into ['ST', 'Interval', 'Generators', 'Generation']
property_col = table.split("__")[-1]  # "Generation"
sol.materialize_table(table, schema="report")

rows = sol.connection.execute(
    f'SELECT name, timestamp, "{property_col}" FROM report."{table}" LIMIT 5'
).fetchall()

for name, ts, val in rows:
    print(name, ts, val)
```

### Reading into pandas

Pass `sol.connection` directly to `pandas.read_sql_query`:

```python
import pandas as pd

table = "ST__Interval__Generators__Generation"
property_col = table.split("__")[-1]  # "Generation"

df = pd.read_sql_query(
    f'SELECT name, timestamp, "{property_col}" FROM report."{table}"',
    sol.connection,
)
```

Filter by object name and date range inside the SQL to avoid pulling large
result sets into memory:

```python
df = pd.read_sql_query(
    f'''
    SELECT name, timestamp, "{property_col}"
    FROM report."{table}"
    WHERE name = ? AND timestamp BETWEEN ? AND ?
    ''',
    sol.connection,
    params=("Coal_Gen", "2017-01-01 00:00:00", "2017-01-08 00:00:00"),
)
```

### Re-opening an existing database

If you already ran `to_sqlite()` once, use `from_sqlite()` to skip the re-import
and go straight to querying:

```python
from plexosdb.solution_reader import PlexosSolution

sol = PlexosSolution.from_sqlite("output.sqlite")

table = "ST__Interval__Generators__Generation"
property_col = table.split("__")[-1]  # "Generation"
sol.materialize_table(table, schema="report")

df = pd.read_sql_query(
    f'SELECT name, timestamp, "{property_col}" FROM report."{table}"',
    sol.connection,
)
sol.close()
```

### Listing available tables before querying

Use `list_tables()` to discover which derived tables exist before deciding what
to materialize:

```python
# All derived tables (data schema naming, but both data and report are the same set)
for t in sol.list_tables(schema="data"):
    print(t.name)

# Filter by keyword
generators = [t for t in sol.list_tables(schema="data") if "Generator" in t.name]
```
