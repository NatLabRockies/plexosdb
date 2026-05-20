"""Entrypoint for the PlexosDB client providing its exports."""

from importlib.metadata import version

from loguru import logger

from .db import PlexosDB, PropertyRecord
from .db_manager import SQLiteManager
from .enums import ClassEnum, CollectionEnum
from .solution_reader import PLEXOS2SQLite, plexos_to_sqlite
from .xml_handler import XMLHandler

__version__ = version("plexosdb")

logger.disable("r2x_core")

__all__ = (
    "ClassEnum",
    "CollectionEnum",
    "PLEXOS2SQLite",
    "PlexosDB",
    "PropertyRecord",
    "SQLiteManager",
    "XMLHandler",
    "plexos_to_sqlite",
)
