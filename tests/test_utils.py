import pytest

from plexosdb.utils import batched, get_sql_query, get_system_object_name, resolve_membership_id
from plexosdb.exceptions import NotFoundError


@pytest.mark.parametrize(
    "fname",
    ["object_query.sql", "property.sql", "property_query.sql", "simple_object_query.sql"],
)
def test_get_default_queries(fname):
    query = get_sql_query(fname)
    assert isinstance(query, str)


def test_batched():
    test_list = list(range(10))

    for element in batched(test_list, 2):
        assert len(element) == 2


def test_get_system_object_name_no_system_objects(db_instance_with_schema):
    db = db_instance_with_schema
    db._db.execute("DELETE FROM t_object WHERE class_id = 1")

    with pytest.raises(NotFoundError, match="No System object found"):
        get_system_object_name(db)


def test_get_system_object_name_multiple_with_default(db_instance_with_schema):
    import uuid

    db = db_instance_with_schema
    db._db.execute(
        "INSERT INTO t_object(name, class_id, GUID) VALUES (?, 1, ?)",
        ("AnotherSystem", str(uuid.uuid4())),
    )

    result = get_system_object_name(db)
    assert result == "System"


def test_get_system_object_name_multiple_no_default(db_instance_with_schema):
    import uuid

    db = db_instance_with_schema
    db._db.execute("UPDATE t_object SET name = 'NEM' WHERE name = 'System'")
    db._db.execute(
        "INSERT INTO t_object(name, class_id, GUID) VALUES (?, 1, ?)",
        ("AnotherSystem", str(uuid.uuid4())),
    )

    with pytest.raises(ValueError, match="Multiple System objects found"):
        get_system_object_name(db)


def test_resolve_membership_id_not_found(db_instance_with_schema):
    from plexosdb.enums import ClassEnum, CollectionEnum

    db = db_instance_with_schema
    db.add_object(ClassEnum.Generator, "TestGen")

    db._db.execute("DELETE FROM t_membership")

    with pytest.raises(NotFoundError, match="Objects not found"):
        resolve_membership_id(
            db,
            "TestGen",
            object_class=ClassEnum.Generator,
            collection=CollectionEnum.Generators,
            parent_class=ClassEnum.System,
        )
