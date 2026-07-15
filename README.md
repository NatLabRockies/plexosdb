### plexosdb

> SQLite-backed Python API for reading, building, and writing PLEXOS XML models
>
> [![image](https://img.shields.io/pypi/v/plexosdb.svg)](https://pypi.python.org/pypi/plexosdb)
> [![image](https://img.shields.io/pypi/l/plexosdb.svg)](https://pypi.python.org/pypi/plexosdb)
> [![image](https://img.shields.io/pypi/pyversions/plexosdb.svg)](https://pypi.python.org/pypi/plexosdb)
> [![CI](https://github.com/NatLabRockies/plexosdb/actions/workflows/CI.yaml/badge.svg)](https://github.com/NatLabRockies/plexosdb/actions/workflows/CI.yaml)
> [![codecov](https://codecov.io/gh/NatLabRockies/plexosdb/branch/main/graph/badge.svg)](https://codecov.io/gh/NatLabRockies/plexosdb)
> [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
> [![Documentation](https://github.com/NatLabRockies/plexosdb/actions/workflows/docs.yaml/badge.svg?branch=main)](https://natlabrockies.github.io/plexosdb/)

plexosdb converts PLEXOS XML input files into an in-memory SQLite database,
giving you a fast, typed Python API to query, create, and modify power system
models programmatically, then write them back to XML.

## Installation

```console
pip install plexosdb
```

Or with [uv](https://docs.astral.sh/uv/):

```console
uv add plexosdb
```

**Python version support:** 3.11, 3.12, 3.13, 3.14

## Quick Start

```python
from plexosdb import PlexosDB, ClassEnum, CollectionEnum

# Load a PLEXOS XML file into an in-memory SQLite database
db = PlexosDB.from_xml("model.xml")

# Query existing objects
generators = db.get_object_names(ClassEnum.Generator)

# Add new objects
db.add_object(ClassEnum.Generator, name="SolarPV_01", category="Renewables")
db.add_object(ClassEnum.Node, name="Bus_1")

# Create memberships between objects
db.add_membership(
    CollectionEnum.GeneratorNodes,
    parent_class=ClassEnum.Generator,
    parent_name="SolarPV_01",
    child_class=ClassEnum.Node,
    child_name="Bus_1",
)

# Export the modified model back to XML
db.to_xml("modified_model.xml")
```

## Versioned Schema Initialization

When creating a brand-new database (not importing XML), you can preload the
matching PLEXOS master template by version:

```python
from plexosdb import PlexosDB

db = PlexosDB()
db.create_schema(version=10)
```

Supported versions: 9, 10, 11, 12.

Accepted inputs include integers, strings, and tuples. For example:

```python
db.create_schema(version="v11.0R4")
db.create_schema(version=(12, 0, 3))
```

## Read PLEXOS Solution ZIP Tables with pandas

```python
from plexosdb import PlexosSolution
import pandas as pd

PLEXOS_SOLUTION = "/path/to/solution.zip"

sol = PlexosSolution.from_zip(PLEXOS_SOLUTION)
sol.to_sqlite("output.sqlite", if_exists="replace")

table = "ST__Interval__Regions__Fixed_Load"
sol.materialize_table(table, schema="report")
df_table = pd.read_sql_query(f'SELECT * FROM report."{table}"', sol.connection)
```

This pattern is useful when you only need a few report/data tables from a large
solution ZIP, because it materializes tables on demand.

## Documentation

Full documentation is available at
[natlabrockies.github.io/plexosdb](https://natlabrockies.github.io/plexosdb/).

## Related Work

For related previous/current work on querying PLEXOS outputs with DuckDB, see
[plexos2duckdb](https://github.com/NatLabRockies/plexos2duckdb).

## Developer Setup

plexosdb uses [uv](https://docs.astral.sh/uv/) for dependency management.

```console
git clone https://github.com/NatLabRockies/plexosdb.git
cd plexosdb
uv sync --all-groups
```

Install the git hooks so your code is checked before making commits:

```console
uv run prek install
```

Run the test suite:

```console
uv run pytest
```

## License

This software is released under a BSD-3-Clause
[License](https://github.com/NatLabRockies/plexosdb/blob/main/LICENSE.txt).

This software was developed under software record SWR-24-90 at the National
Renewable Energy Laboratory ([NREL](https://www.nrel.gov)).

## Disclaimer

PLEXOS is a registered trademark of Energy Exemplar Pty Ltd. Energy Exemplar Pty
Ltd. has no affiliation to or participation in this software. Reference herein
to any specific commercial products, process, or service by trade name,
trademark, manufacturer, or otherwise, does not necessarily constitute or imply
its endorsement, recommendation, or favoring by the United States Government or
Alliance for Sustainable Energy, LLC ("Alliance"). The views and opinions of
authors expressed in the available or referenced documents do not necessarily
state or reflect those of the United States Government or Alliance.
