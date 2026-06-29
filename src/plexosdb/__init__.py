"""Entrypoint for the PlexosDB client providing its exports."""

from importlib.metadata import version

from loguru import logger

from .db import PlexosDB, PropertyRecord
from .db_manager import SQLiteManager
from .db_solution import PlexosSolution
from .db_solution_models import (
    DuckDBResult,
    DuckDBSchema,
    DuckDBSolutionInfo,
    IfExists,
    ResultPeriod,
    ResultPhase,
    ResultSchema,
    ResultTable,
    TableInfo,
    TableType,
)
from .enums import ClassEnum, CollectionEnum
from .xml_handler import XMLHandler

__version__ = version("plexosdb")

logger.disable("r2x_core")

__all__ = (
    "ClassEnum",
    "CollectionEnum",
    "DuckDBResult",
    "DuckDBSchema",
    "DuckDBSolutionInfo",
    "IfExists",
    "PlexosDB",
    "PlexosSolution",
    "PropertyRecord",
    "ResultPeriod",
    "ResultPhase",
    "ResultSchema",
    "ResultTable",
    "TableInfo",
    "TableType",
    "XMLHandler",
)
