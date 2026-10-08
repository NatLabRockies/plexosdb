"""Custom PlexosDB exceptions that highlight domain-specific failures."""


class NotFoundError(Exception):
    """Raised when the database cannot locate a requested entry."""


class MultlipleElementsError(Exception):
    """Raised when a query unexpectedly returns multiple elements."""


class ModelError(Exception):
    """Raised for generic errors related to model relationships."""


class DatabaseValidationError(ModelError):
    """Raised when database validation finds integrity or consistency issues."""

    def __init__(self, findings: dict[str, list[str]]) -> None:
        """Create an error carrying findings grouped by validation category."""
        self.findings = {category: list(messages) for category, messages in findings.items()}
        details = "\n".join(
            f"- [{category}] {message}"
            for category, messages in self.findings.items()
            for message in messages
        )
        super().__init__(f"Database validation failed:\n{details}")


class MultipleFilesError(Exception):
    """Raised when multiple files are provided but only one is expected."""


class NameError(ValueError):
    """Raised when an object name is invalid or missing in context."""


class NoPropertiesError(Exception):
    """Raised when a lookup finds no properties for a given object."""


class PropertyError(Exception):
    """Raised when we have a problem with a property."""
