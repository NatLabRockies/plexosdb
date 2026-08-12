from pathlib import Path

import pytest

from plexosdb import ClassEnum, PlexosDB
from plexosdb.exceptions import NotFoundError


XML_PATH = Path(__file__).parent / "data" / "run_of_river_case" / "TestSystem.xml"


@pytest.fixture
def run_of_river_db():
    db = PlexosDB.from_xml(XML_PATH)
    yield db
    db._db.close()


def _property_rows(db: PlexosDB, object_name: str, property_name: str) -> list[tuple]:
    return db.query(
        """
        SELECT d.value, COALESCE(b.band_id, 1)
        FROM t_data AS d
        JOIN t_membership AS m ON m.membership_id = d.membership_id
        JOIN t_object AS o ON o.object_id = m.child_object_id
        JOIN t_property AS p ON p.property_id = d.property_id
        LEFT JOIN t_band AS b ON b.data_id = d.data_id
        WHERE o.name = ? AND p.name = ?
        ORDER BY COALESCE(b.band_id, 1)
        """,
        (object_name, property_name),
    )


def test_update_property_updates_xml_fixture_value(run_of_river_db: PlexosDB) -> None:
    run_of_river_db.update_property(
        "Coal_Gen",
        "Max Capacity",
        625.0,
        object_class=ClassEnum.Generator,
    )

    rows = _property_rows(run_of_river_db, "Coal_Gen", "Max Capacity")
    assert rows == [(625.0, 1)]


def test_update_property_only_updates_requested_band(run_of_river_db: PlexosDB) -> None:
    run_of_river_db.update_property(
        "Gas_Gen2",
        "Load Point",
        95.0,
        object_class=ClassEnum.Generator,
        band=2,
    )

    rows = _property_rows(run_of_river_db, "Gas_Gen2", "Load Point")
    assert rows == [
        (95.0 if band == 2 else 50.0 + 20.0 * band, band)
        for band in range(1, 11)
    ]


def test_update_properties_updates_multiple_xml_fixture_values(run_of_river_db: PlexosDB) -> None:
    run_of_river_db.update_properties(
        [
            {
                "object_name": "Coal_Gen",
                "property_name": "Max Capacity",
                "new_value": 625.0,
                "object_class": ClassEnum.Generator,
            },
            {
                "object_name": "Gas_Gen1",
                "property_name": "Max Capacity",
                "new_value": 325.0,
                "object_class": ClassEnum.Generator,
            },
        ]
    )

    assert _property_rows(run_of_river_db, "Coal_Gen", "Max Capacity") == [(625.0, 1)]
    assert _property_rows(run_of_river_db, "Gas_Gen1", "Max Capacity") == [(325.0, 1)]


def test_update_property_raises_for_missing_fixture_property(run_of_river_db: PlexosDB) -> None:
    with pytest.raises(NotFoundError):
        run_of_river_db.update_property(
            "Coal_Gen",
            "Max Capacity",
            625.0,
            object_class=ClassEnum.Generator,
            band=99,
        )