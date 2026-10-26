"""Custom PlexosDB exceptions and structured error details."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
import os
import sys


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
    """Raised when database validation finds integrity or consistency issues.

    WARN labels are yellow when stderr is a terminal, unless NO_COLOR is set.
    Redirected output remains plain text.
    """

    def __init__(self, findings: Iterable[DatabaseValidationFinding]) -> None:
        """Create an error carrying typed findings."""
        self.findings = tuple(findings)
        warning = "\033[33mWARN\033[0m" if sys.stderr.isatty() and "NO_COLOR" not in os.environ else "WARN"
        details = "\n".join(
            f"{warning}: [{finding.category.value}] {finding.message}" for finding in self.findings
        )
        super().__init__(
            f"Database validation results:\n{details}\nValidation found {len(self.findings)} errors."
        )


class MultipleFilesError(Exception):
    """Raised when multiple files are provided but only one is expected."""


class NameError(ValueError):
    """Raised when an object name is invalid or missing in context."""


class NoPropertiesError(Exception):
    """Raised when a lookup finds no properties for a given object."""


class PropertyError(Exception):
    """Raised when we have a problem with a property."""
