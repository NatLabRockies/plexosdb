from __future__ import annotations

from plexosdb.checks import check_memberships_from_records


def test_check_memberships_from_records_valid_payload() -> None:
    records = [
        {
            "parent_class_id": 1,
            "parent_object_id": 2,
            "collection_id": 3,
            "child_class_id": 4,
            "child_object_id": 5,
        }
    ]

    assert check_memberships_from_records(records) is True


def test_check_memberships_from_records_invalid_payload() -> None:
    records = [
        {
            "parent_class_id": 1,
            "parent_object_id": 2,
            "collection_id": 3,
            "child_class_id": 4,
            "bad_key": 5,
        }
    ]

    assert check_memberships_from_records(records) is False
