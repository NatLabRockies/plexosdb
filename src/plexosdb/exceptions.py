"""Custom PlexosDB exceptions and structured error details."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class NotFoundError(Exception):
    """Raised when the database cannot locate a requested entry."""


class MultlipleElementsError(Exception):
    """Raised when a query unexpectedly returns multiple elements."""


class ModelError(Exception):
    """Raised for generic errors related to model relationships."""


class DatabaseValidationCategory(StrEnum):
    """Stable categories for database validation findings."""

    SQLITE = "sqlite"
    FOREIGN_KEYS = "foreign_keys"
    SCHEMA = "schema"
    OBJECTS = "objects"
    MEMBERSHIPS = "memberships"
    ATTRIBUTES = "attributes"
    PROPERTIES = "properties"
    TYPES = "types"


@dataclass(frozen=True, slots=True, kw_only=True)
class DatabaseValidationFinding:
    """One structured finding produced by database validation."""

    category: DatabaseValidationCategory
    message: str


class DatabaseValidationError(ModelError):
    """Raised when database validation finds integrity or consistency issues."""

    def __init__(self, findings: Iterable[DatabaseValidationFinding]) -> None:
        """Create an error carrying typed findings."""
        self.findings = tuple(findings)
        details = "\n".join(f"- [{finding.category.value}] {finding.message}" for finding in self.findings)
        super().__init__(f"Database validation failed:\n{details}")


class MultipleFilesError(Exception):
    """Raised when multiple files are provided but only one is expected."""


class NameError(ValueError):
    """Raised when an object name is invalid or missing in context."""


class NoPropertiesError(Exception):
    """Raised when a lookup finds no properties for a given object."""


class PropertyError(Exception):
    """Raised when we have a problem with a property."""
