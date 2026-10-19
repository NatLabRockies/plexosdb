"""Optional numeric metadata defaults at solution-consumer boundaries."""

import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import pytest

from plexosdb import XMLRecord
from plexosdb.solution_reader import PlexosSolution, _build_key_period_map, _resolve_report_unit


def write_metadata_zip(tables: dict[str, list[XMLRecord]], /, *, destination: Path) -> Path:
    root = ET.Element("MasterDataSet")
    for table, records in tables.items():
        for record in records:
            row = ET.SubElement(root, table)
            for name, value in record.items():
                ET.SubElement(row, name).text = value
    with ZipFile(destination, "w") as zipped:
        zipped.writestr("solution.xml", ET.tostring(root, encoding="utf-8"))
    return destination


@pytest.mark.parametrize(
    "period, expected", [(None, None), ("", None), (" \t\n", None), ("\u00a0", None), (" 0 ", 0)]
)
def test_optional_key_index_period_keeps_missing_default(
    tmp_path: Path, period: str | None, expected: int | None
) -> None:
    archive = write_metadata_zip(
        {"t_key_index": [{"key_id": "1", "period_type_id": period}]},
        destination=tmp_path / "period.zip",
    )
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite(decode_bin_values=False)
        assert solution.connection.execute("SELECT period_type_id FROM t_key_index").fetchone() == (
            period or None,
        )
        assert _build_key_period_map(
            solution.connection, has_key_period=False, key_index_cols=["key_id", "period_type_id"]
        ) == {1: expected}


@pytest.mark.parametrize(
    "regular, summary, expected",
    [
        ("0070", None, "MW"),
        ("0070", " \t\n", "MW"),
        ("0070", "0", "-"),
        ("0070", " 00071 ", "GW"),
        (" \t\n", None, None),
        (" \t\n", "71", "GW"),
        ("0", None, "-"),
    ],
)
def test_blank_unit_references_do_not_match_unit_zero(
    tmp_path: Path, regular: str, summary: str | None, expected: str | None
) -> None:
    archive = write_metadata_zip(
        {
            "t_key": [{"key_id": "1", "property_id": "1", "is_summary": "1"}],
            "t_property": [{"property_id": "1", "unit_id": regular, "summary_unit_id": summary}],
            "t_unit": [
                {"unit_id": "0", "value": "-"},
                {"unit_id": "70", "value": "MW"},
                {"unit_id": "71", "value": "GW"},
            ],
        },
        destination=tmp_path / "units.zip",
    )
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite(decode_bin_values=False)
        assert _resolve_report_unit(solution.connection, key_ids={1}) == expected
        assert solution.connection.execute("SELECT unit_id, summary_unit_id FROM t_property").fetchone() == (
            regular,
            summary,
        )
