from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from plexosdb import ClassEnum, PlexosDB
from plexosdb.exceptions import NotFoundError

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def db() -> Iterator[PlexosDB]:
    database = PlexosDB()
    database.create_schema(version=10)
    yield database


def _add_generator_property(db: PlexosDB, value: str | float = 10.0) -> int:
    db.add_object(ClassEnum.Generator, "Generator1")
    return db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", value)


def test_add_time_slice_creates_native_include_ranges(db: PlexosDB) -> None:
    timeslice_id = db.add_time_slice(
        "Peak",
        interval="PT1H",
        start_datetime="2024-01-01T00:00:00",
        end_datetime="2024-01-01T02:30:00",
        description="Peak hours",
    )

    rows = db.query(
        """
        SELECT d.value, date_from.date, date_to.date
        FROM t_data d
        JOIN t_membership m ON m.membership_id = d.membership_id
        JOIN t_property p ON p.property_id = d.property_id
        JOIN t_date_from date_from ON date_from.data_id = d.data_id
        JOIN t_date_to date_to ON date_to.data_id = d.data_id
        WHERE m.child_object_id = ? AND p.name = 'Include'
        ORDER BY d.data_id
        """,
        (timeslice_id,),
    )

    assert rows == [
        (-1.0, "2024-01-01T00:00:00", "2024-01-01T01:00:00"),
        (-1.0, "2024-01-01T01:00:00", "2024-01-01T02:00:00"),
        (-1.0, "2024-01-01T02:00:00", "2024-01-01T02:30:00"),
    ]
    assert db.query("SELECT description FROM t_object WHERE object_id = ?", (timeslice_id,)) == [
        ("Peak hours",)
    ]


@pytest.mark.parametrize(
    ("interval", "start_datetime", "end_datetime"),
    [
        ("PT0S", "2024-01-01T00:00:00", "2024-01-01T01:00:00"),
        ("PT1H", "2024-01-02T00:00:00", "2024-01-01T00:00:00"),
        ("PT1H", "not-a-date", "2024-01-01T01:00:00"),
    ],
)
def test_add_time_slice_rejects_invalid_interval_or_range(
    db: PlexosDB, interval: str, start_datetime: str, end_datetime: str
) -> None:
    with pytest.raises(ValueError):
        db.add_time_slice(
            "Invalid",
            interval=interval,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    assert not db.list_objects_by_class(ClassEnum.Timeslice)


def test_add_variable_tag_links_variable_and_optionally_updates_value(db: PlexosDB) -> None:
    data_id = _add_generator_property(db)
    variable_id = db.add_object(ClassEnum.Variable, "LoadProfile")

    assert db.add_variable_tag(data_id, "LoadProfile", value=15.5) == data_id
    assert db.query("SELECT value FROM t_data WHERE data_id = ?", (data_id,)) == [(15.5,)]
    assert db.query("SELECT object_id FROM t_tag WHERE data_id = ?", (data_id,)) == [(variable_id,)]

    next_data_id = db.add_property(ClassEnum.Generator, "Generator1", "Max Capacity", 20.0)
    db.add_variable_tag(next_data_id, "LoadProfile")
    assert db.query("SELECT value FROM t_data WHERE data_id = ?", (next_data_id,)) == [(20.0,)]


def test_add_variable_tag_requires_existing_data_and_variable(db: PlexosDB) -> None:
    data_id = _add_generator_property(db)

    with pytest.raises(NotFoundError, match="Variable"):
        db.add_variable_tag(data_id, "MissingVariable")
    with pytest.raises(NotFoundError, match="Data record"):
        db.add_variable_tag(data_id + 1, "MissingVariable")


def test_set_date_range_upserts_supplied_boundaries_and_preserves_others(db: PlexosDB) -> None:
    data_id = _add_generator_property(db)
    db.set_date_range(data_id, date_from="2024-01-01T00:00:00", date_to="2024-12-31T23:00:00")
    db.set_date_range(data_id, date_to="2025-12-31T23:00:00")

    assert db.query("SELECT date FROM t_date_from WHERE data_id = ?", (data_id,)) == [
        ("2024-01-01T00:00:00",)
    ]
    assert db.query("SELECT date FROM t_date_to WHERE data_id = ?", (data_id,)) == [("2025-12-31T23:00:00",)]


def test_set_date_range_rejects_reversed_or_missing_records(db: PlexosDB) -> None:
    data_id = _add_generator_property(db)

    with pytest.raises(ValueError, match="date_from"):
        db.set_date_range(data_id, date_from="2024-02-01", date_to="2024-01-01")
    with pytest.raises(NotFoundError, match="Data record"):
        db.set_date_range(data_id + 1, date_from="2024-01-01")


@pytest.mark.parametrize(
    ("boundary", "value", "error"),
    [
        ("date_from", "2025-01-01", "date_from must not be later"),
        ("date_to", "2023-12-31", "date_from must not be later"),
        ("date_from", "2024-06-01T00:00:00+00:00", "compatible time zones"),
        ("date_to", "2024-06-01T00:00:00+00:00", "compatible time zones"),
    ],
)
def test_set_date_range_validates_single_boundary_against_stored_opposite(
    db: PlexosDB, boundary: str, value: str, error: str
) -> None:
    data_id = _add_generator_property(db)
    db.set_date_range(data_id, date_from="2024-01-01", date_to="2024-12-31")

    with pytest.raises(ValueError, match=error):
        db.set_date_range(data_id, **{boundary: value})

    assert db.query("SELECT date FROM t_date_from WHERE data_id = ?", (data_id,)) == [("2024-01-01",)]
    assert db.query("SELECT date FROM t_date_to WHERE data_id = ?", (data_id,)) == [("2024-12-31",)]


@pytest.mark.parametrize(
    ("boundary", "value"),
    [("date_from", "2024-12-31"), ("date_to", "2024-01-01")],
)
def test_set_date_range_accepts_single_boundary_equal_to_stored_opposite(
    db: PlexosDB, boundary: str, value: str
) -> None:
    data_id = _add_generator_property(db)
    db.set_date_range(data_id, date_from="2024-01-01", date_to="2024-12-31")

    db.set_date_range(data_id, **{boundary: value})

    assert db.query(f"SELECT date FROM t_{boundary} WHERE data_id = ?", (data_id,)) == [(value,)]


@pytest.mark.parametrize(("boundary", "opposite"), [("date_from", "date_to"), ("date_to", "date_from")])
@pytest.mark.parametrize("null_row", [False, True])
def test_set_date_range_allows_missing_opposite_boundary(
    db: PlexosDB, boundary: str, opposite: str, null_row: bool
) -> None:
    data_id = _add_generator_property(db)
    if null_row:
        db._db.execute(f"INSERT INTO t_{opposite} (data_id, date) VALUES (?, NULL)", (data_id,))

    db.set_date_range(data_id, **{boundary: "2024-01-01"})

    assert db.query(f"SELECT date FROM t_{boundary} WHERE data_id = ?", (data_id,)) == [("2024-01-01",)]


def test_set_date_range_replaces_both_old_boundaries(db: PlexosDB) -> None:
    data_id = _add_generator_property(db)
    db.set_date_range(data_id, date_from="2024-01-01", date_to="2024-12-31")

    db.set_date_range(data_id, date_from="2025-01-01", date_to="2025-12-31")

    assert db.query("SELECT date FROM t_date_from WHERE data_id = ?", (data_id,)) == [("2025-01-01",)]
    assert db.query("SELECT date FROM t_date_to WHERE data_id = ?", (data_id,)) == [("2025-12-31",)]


def test_set_date_range_compares_timezone_offsets(db: PlexosDB) -> None:
    data_id = _add_generator_property(db)
    db.set_date_range(data_id, date_to="2024-01-01T10:00:00+00:00")

    db.set_date_range(data_id, date_from="2024-01-01T11:00:00+02:00")
    with pytest.raises(ValueError, match="date_from must not be later"):
        db.set_date_range(data_id, date_from="2024-01-01T11:00:00+00:00")
    assert db.query("SELECT date FROM t_date_from WHERE data_id = ?", (data_id,)) == [
        ("2024-01-01T11:00:00+02:00",)
    ]


def test_update_and_delete_text_preserve_other_fields_and_report_missing_rows(db: PlexosDB) -> None:
    data_id = _add_generator_property(db)
    class_id = db.get_class_id(ClassEnum.Node)
    db._db.execute(
        "INSERT INTO t_text(data_id, class_id, value, state) VALUES (?, ?, ?, ?)",
        (data_id, class_id, "before", 2),
    )

    db.update_text(data_id, "after", class_id=class_id)
    assert db.get_text(data_id, class_id=class_id) == [
        {"data_id": data_id, "class_id": class_id, "value": "after", "state": 2, "action_id": None}
    ]

    db.delete_text(data_id, class_id=class_id)
    assert db.get_text(data_id, class_id=class_id) == []
    with pytest.raises(NotFoundError, match="Text record"):
        db.delete_text(data_id, class_id=class_id)
    with pytest.raises(NotFoundError, match="Text record"):
        db.update_text(data_id, "missing", class_id=class_id)
