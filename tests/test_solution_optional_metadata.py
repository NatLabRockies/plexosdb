"""Optional numeric metadata defaults at solution-consumer boundaries."""

import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

import pytest

from plexosdb import XMLRecord
from plexosdb.solution_reader import PlexosSolution, _build_key_period_map, _resolve_report_unit
from plexosdb.solution_reader import _build_derived_table_map
from plexosdb.solution_reader.utils import integer_reference_sql


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
@pytest.mark.parametrize("use_key_period", [False, True])
def test_optional_period_keeps_missing_default(
    tmp_path: Path, period: str | None, expected: int | None, use_key_period: bool
) -> None:
    table = "t_key" if use_key_period else "t_key_index"
    tables: dict[str, list[XMLRecord]] = {table: [{"key_id": "1", "period_type_id": period}]}
    if use_key_period:
        tables["t_key_index"] = [{"key_id": "1"}]
    archive = write_metadata_zip(
        tables,
        destination=tmp_path / "period.zip",
    )
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite(decode_bin_values=False)
        assert solution.connection.execute(f"SELECT period_type_id FROM {table}").fetchone() == (
            period or None,
        )
        assert _build_key_period_map(
            solution.connection,
            has_key_period=use_key_period,
            key_index_cols=["key_id"] if use_key_period else ["key_id", "period_type_id"],
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
        ("0070", "\u00a0", "MW"),
        ("\u00a00070\u00a0", None, "MW"),
        ("\u00a0", None, None),
        ("0070", "\u00a00071\u00a0", "GW"),
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


@pytest.mark.parametrize(
    "reference, sample, category, child_name",
    [
        (None, "Mean", None, None),
        (" \t\n", "Mean", None, None),
        ("\u00a0", "Mean", None, None),
        ("0", "Zero", "Zero category", "Zero generator"),
        ("\u00a01\u00a0", "Peak", "Category", "Generator"),
    ],
)
@pytest.mark.parametrize("sample_label", ["Peak", " \t\n", "\u00a0", " Peak "])
@pytest.mark.parametrize("padded_ids", [False, True])
@pytest.mark.parametrize("variable_child", [False, True])
def test_optional_references_preserve_defaults_and_explicit_zero(
    tmp_path: Path,
    reference: str | None,
    sample: str,
    category: str | None,
    child_name: str | None,
    padded_ids: bool,
    sample_label: str,
    variable_child: bool,
) -> None:
    if sample == "Peak":
        sample = sample_label if sample_label.strip() else "Mean"
    one = "\u00a01\u00a0" if padded_ids else "1"
    child_reference = reference if variable_child else "1"
    expected_name = child_name if variable_child else "Generator"
    archive = write_metadata_zip(
        {
            "t_key_index": [{"key_id": "1", "period_type_id": "0"}],
            "t_key": [
                {
                    "key_id": one,
                    "membership_id": "1",
                    "property_id": "1",
                    "sample_id": reference,
                    "band_id": "1",
                    "phase_id": "4",
                    "is_summary": "0",
                }
            ],
            "t_membership": [
                {"membership_id": one, "child_object_id": child_reference, "collection_id": "1"}
            ],
            "t_collection": [{"collection_id": one, "name": "Generators"}],
            "t_property": [
                {"property_id": one, "name": "Generation", "unit_id": "70", "summary_unit_id": "70"}
            ],
            "t_object": [
                {"object_id": "0", "name": "Zero generator", "category_id": "0"},
                {"object_id": one, "name": "Generator", "category_id": reference},
            ],
            "t_sample": [
                {"sample_id": "0", "sample_name": "Zero"},
                {"sample_id": one, "sample_name": sample_label},
            ],
            "t_category": [
                {"category_id": "0", "name": "Zero category"},
                {"category_id": one, "name": "Category"},
            ],
            "t_unit": [{"unit_id": "70", "value": "MW"}],
        },
        destination=tmp_path / "references.zip",
    )
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite(decode_bin_values=False)
        solution.connection.execute(
            "CREATE TABLE t_data_values(key_id INTEGER, period_type_id INTEGER, block_id INTEGER, value REAL)"
        )
        solution.connection.execute("INSERT INTO t_data_values VALUES (1, 0, 1, 10.5)")
        solution.connection.execute(
            "CREATE INDEX idx_t_sample_sample_id_numeric ON t_sample(CAST(sample_id AS INTEGER))"
        )
        assert solution.materialize_table("ST__Interval__Generators__Generation").created
        assert solution.connection.execute(
            "SELECT name, sample_name, category, Generation "
            'FROM report."ST__Interval__Generators__Generation"'
        ).fetchall() == [(expected_name, sample, category, 10.5)]
        assert solution.connection.execute("SELECT sample_id FROM t_key").fetchone() == (reference,)
        assert solution.connection.execute(
            "SELECT sample_name FROM t_sample WHERE sample_name IS NOT 'Zero'"
        ).fetchone() == (sample_label,)
        assert solution.connection.execute(
            "SELECT category_id FROM t_object WHERE name='Generator'"
        ).fetchone() == (reference,)
        assert solution.connection.execute("SELECT child_object_id FROM t_membership").fetchone() == (
            child_reference,
        )
        plan = solution.connection.execute(
            f"EXPLAIN QUERY PLAN SELECT * FROM t_sample WHERE {integer_reference_sql('sample_id')} = ?",
            (1,),
        ).fetchall()
        assert any("idx_t_sample_sample_id_reference" in row[3] for row in plan)


@pytest.mark.parametrize("summary_name", [" \t\n", "\u00a0"])
def test_blank_summary_names_keep_distinct_property_tables(tmp_path: Path, summary_name: str) -> None:
    archive = write_metadata_zip(
        {
            "t_key_index": [{"key_id": "1", "period_type_id": "0"}, {"key_id": "2", "period_type_id": "0"}],
            "t_key": [
                {
                    "key_id": str(key),
                    "membership_id": "1",
                    "property_id": str(key),
                    "phase_id": "4",
                    "is_summary": "1",
                }
                for key in (1, 2)
            ],
            "t_membership": [{"membership_id": "1", "collection_id": "1"}],
            "t_collection": [{"collection_id": "1", "name": "Generators"}],
            "t_property": [
                {"property_id": "1", "name": "Generation", "summary_name": summary_name},
                {"property_id": "2", "name": "Load", "summary_name": summary_name},
            ],
        },
        destination=tmp_path / "properties.zip",
    )
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite(decode_bin_values=False)
        assert _build_derived_table_map(solution.connection) == {
            ("data", "ST__Interval__Generators__Generation"): {1},
            ("data", "ST__Interval__Generators__Load"): {2},
        }
        assert solution.connection.execute(
            "SELECT summary_name FROM t_property ORDER BY rowid"
        ).fetchall() == [(summary_name,), (summary_name,)]


@pytest.mark.parametrize("blank", [None, "", " \t\n", "\u00a0"])
@pytest.mark.parametrize("summary_flag", [None, "1"])
def test_blank_unit_labels_keep_fallback(tmp_path: Path, blank: str | None, summary_flag: str | None) -> None:
    key: XMLRecord = {"key_id": "1", "property_id": "1"}
    if summary_flag is not None:
        key["is_summary"] = summary_flag
    regular = " MW " if summary_flag else blank
    summary = blank if summary_flag else " GW "
    archive = write_metadata_zip(
        {
            "t_key": [key],
            "t_property": [{"property_id": "1", "unit_id": "70", "summary_unit_id": "71"}],
            "t_unit": [{"unit_id": "70", "value": regular}, {"unit_id": "71", "value": summary}],
        },
        destination=tmp_path / "blank-labels.zip",
    )
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite(decode_bin_values=False)
        assert _resolve_report_unit(solution.connection, key_ids={1}) == (" MW " if summary_flag else " GW ")
        assert solution.connection.execute("SELECT value FROM t_unit ORDER BY unit_id").fetchall() == [
            (regular or None,),
            (summary or None,),
        ]
