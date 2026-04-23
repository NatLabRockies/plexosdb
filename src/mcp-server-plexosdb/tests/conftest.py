"""Pytest fixtures for mcp-server-plexosdb tests."""

from __future__ import annotations

from pathlib import Path

import pytest

# Path to the plexosdb test data folder (reused for XML fixtures).
_PLEXOSDB_ROOT = Path(__file__).resolve().parents[3]
_DATA_FOLDER = _PLEXOSDB_ROOT / "tests" / "data"


@pytest.fixture(scope="session")
def data_folder() -> Path:
    """Return the plexosdb tests/data folder with bundled sample XMLs."""
    return _DATA_FOLDER
