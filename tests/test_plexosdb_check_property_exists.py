"""Tests for the standalone check_property_exists function."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import plexosdb.checks as checks_module

if TYPE_CHECKING:
    from plexosdb import PlexosDB


def test_check_property_exists_valid_single(db_thermal_gen: PlexosDB) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    result = checks_module.check_property_exists(
        db_thermal_gen, CollectionEnum.Generators, ClassEnum.Generator, "Max Capacity"
    )

    assert result is True


def test_check_property_exists_valid_multiple(db_thermal_gen: PlexosDB) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    result = checks_module.check_property_exists(
        db_thermal_gen,
        CollectionEnum.Generators,
        ClassEnum.Generator,
        ["Max Capacity", "Fuel Price", "Heat Rate"],
    )

    assert result is True


def test_check_property_exists_invalid_collection_raises_error(
    db_with_topology: PlexosDB,
) -> None:
    from plexosdb import ClassEnum
    from plexosdb.exceptions import NotFoundError

    with pytest.raises(NotFoundError, match=r"Collection.*does not exist"):
        checks_module.check_property_exists(
            db_with_topology,
            "InvalidCollection",
            ClassEnum.Generator,
            "Max Capacity",
        )


def test_check_property_exists_invalid_child_class_raises_error(
    db_with_topology: PlexosDB,
) -> None:
    from plexosdb import CollectionEnum
    from plexosdb.exceptions import NotFoundError

    with pytest.raises(NotFoundError, match=r"Child class.*does not exist"):
        checks_module.check_property_exists(
            db_with_topology,
            CollectionEnum.Generators,
            "InvalidClass",
            "Max Capacity",
        )


def test_check_property_exists_invalid_property_returns_false(
    db_thermal_gen: PlexosDB,
) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    result = checks_module.check_property_exists(
        db_thermal_gen, CollectionEnum.Generators, ClassEnum.Generator, "Invalid Property"
    )

    assert result is False


def test_check_property_exists_mixed_valid_invalid_returns_false(
    db_thermal_gen: PlexosDB,
) -> None:
    from plexosdb import ClassEnum, CollectionEnum

    result = checks_module.check_property_exists(
        db_thermal_gen,
        CollectionEnum.Generators,
        ClassEnum.Generator,
        ["Max Capacity", "Invalid Property"],
    )

    assert result is False
