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
    ResultSchema,
    ResultTable,
    TableInfo,
)
from .enums import ClassEnum, CollectionEnum, PeriodEnum, PhaseEnum, TableTypeEnum
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
    "PeriodEnum",
    "PhaseEnum",
    "PlexosDB",
    "PlexosSolution",
    "PropertyRecord",
    "ResultSchema",
    "ResultTable",
    "TableInfo",
    "TableTypeEnum",
    "XMLHandler",
)
