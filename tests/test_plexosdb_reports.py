from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from plexosdb.db import PlexosDB


def test_list_valid_property_report(db_base: PlexosDB):
    from plexosdb import ClassEnum, CollectionEnum

    db: PlexosDB = db_base
    result = db.list_valid_properties_report(
        CollectionEnum.Generators, parent_class_enum=ClassEnum.System, child_class_enum=ClassEnum.Generator
    )
    assert result
    assert len(result) > 1  # Reports vary by revision


def test_adding_reports(db_base: PlexosDB):
    from plexosdb import ClassEnum, CollectionEnum
    from plexosdb.exceptions import NameError

    db: PlexosDB = db_base

    test_object = "test_report"
    property = "Units"
    _ = db.add_object(ClassEnum.Report, name=test_object)
    db.add_report(
        object_name=test_object,
        property=property,
        collection=CollectionEnum.Generators,
        parent_class=ClassEnum.System,
        child_class=ClassEnum.Generator,
    )

    with pytest.raises(NameError):
        db.add_report(
            object_name=test_object,
            property="WrongProperty",
            collection=CollectionEnum.Generators,
            parent_class=ClassEnum.System,
            child_class=ClassEnum.Generator,
        )


def test_add_report_property_to_existing_report(db_base: PlexosDB):
    from plexosdb import ClassEnum, CollectionEnum

    db: PlexosDB = db_base
    report_object = "existing_report"
    db.add_object(ClassEnum.Report, name=report_object)

    report_properties = db.list_valid_properties_report(
        CollectionEnum.Generators,
        parent_class_enum=ClassEnum.System,
        child_class_enum=ClassEnum.Generator,
    )
    first_property, second_property = report_properties[:2]

    for report_property in (first_property, second_property):
        db.add_report(
            object_name=report_object,
            property=report_property,
            collection=CollectionEnum.Generators,
            parent_class=ClassEnum.System,
            child_class=ClassEnum.Generator,
        )

    configured_properties = db.query(
        """
        SELECT property_report.name
        FROM t_report AS report
        JOIN t_object AS object ON object.object_id = report.object_id
        JOIN t_property_report AS property_report
            ON property_report.property_id = report.property_id
        WHERE object.name = ?
        ORDER BY property_report.name
        """,
        (report_object,),
    )

    assert [row[0] for row in configured_properties] == sorted((first_property, second_property))
