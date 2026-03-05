"""Benchmark coverage for bulk membership insertion."""

from __future__ import annotations

import uuid

import pytest

from plexosdb import ClassEnum, CollectionEnum, PlexosDB


def _insert_objects(
    db: PlexosDB,
    *,
    class_id: int,
    count: int,
    prefix: str,
    start_id: int,
) -> list[int]:
    object_ids = [start_id + idx for idx in range(count)]
    params = [
        (object_id, f"{prefix}_{idx}", class_id, str(uuid.uuid4()))
        for idx, object_id in enumerate(object_ids)
    ]
    db._db.executemany("INSERT INTO t_object(object_id, name, class_id, GUID) VALUES (?, ?, ?, ?)", params)
    return object_ids


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("record_count", "chunksize", "rounds"),
    [
        pytest.param(100, 100, 10, id="small"),
        pytest.param(1_000, 1_000, 10, id="medium"),
        pytest.param(10_000, 10_000, 10, id="large"),
        pytest.param(300_000, 10_000, 2, id="xlarge_300k"),
    ],
)
def test_add_memberships_from_records_benchmark(
    benchmark,
    db_instance_with_schema: PlexosDB,
    record_count: int,
    chunksize: int,
    rounds: int,
) -> None:
    """Benchmark `add_memberships_from_records` across different payload sizes."""
    db = db_instance_with_schema
    parent_class_id = db.get_class_id(ClassEnum.Generator)
    child_class_id = db.get_class_id(ClassEnum.Node)
    collection_id = db.get_collection_id(
        CollectionEnum.Nodes,
        parent_class_enum=ClassEnum.Generator,
        child_class_enum=ClassEnum.Node,
    )
    parent_ids = _insert_objects(
        db,
        class_id=parent_class_id,
        count=1,
        prefix=f"benchmark_parent_{record_count}",
        start_id=10_000,
    )
    child_ids = _insert_objects(
        db,
        class_id=child_class_id,
        count=record_count,
        prefix=f"benchmark_child_{record_count}",
        start_id=50_000,
    )
    records = [
        {
            "parent_class_id": parent_class_id,
            "parent_object_id": parent_ids[0],
            "collection_id": collection_id,
            "child_class_id": child_class_id,
            "child_object_id": child_id,
        }
        for child_id in child_ids
    ]

    def _reset_memberships() -> None:
        db._db.execute(
            (
                "DELETE FROM t_membership "
                "WHERE collection_id = ? AND parent_class_id = ? AND child_class_id = ?"
            ),
            (collection_id, parent_class_id, child_class_id),
        )

    result = benchmark.pedantic(
        db.add_memberships_from_records,
        args=(records,),
        kwargs={"chunksize": chunksize},
        setup=_reset_memberships,
        rounds=rounds,
        iterations=1,
    )
    assert result is True
