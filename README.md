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

## Documentation

Full documentation is available at
[natlabrockies.github.io/plexosdb](https://natlabrockies.github.io/plexosdb/).

## Developer Setup

plexosdb uses [uv](https://docs.astral.sh/uv/) for dependency management.

```console
git clone https://github.com/NatLabRockies/plexosdb.git
cd plexosdb
uv sync --all-groups
```

Install the pre-commit hooks so your code is checked before making commits:

```console
uv run pre-commit install
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
