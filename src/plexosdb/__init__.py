"""Entrypoint for the PlexosDB client providing its exports."""

from importlib.metadata import version

from loguru import logger

from .db import PlexosDB, PropertyRecord
from .db_manager import SQLiteManager
from .enums import ClassEnum, CollectionEnum
from .solution_reader import PlexosSolution, show_db_tables
from .solution_reader import MaterializeResult, SolutionInfo, SQLiteResult, TableInfo
from .xml_handler import XMLHandler

__version__ = version("plexosdb")

logger.disable("r2x_core")

__all__ = (
    "ClassEnum",
    "CollectionEnum",
    "MaterializeResult",
    "PlexosDB",
    "PlexosSolution",
    "PropertyRecord",
    "SQLiteResult",
    "SolutionInfo",
    "TableInfo",
    "XMLHandler",
    "show_db_tables",
)
