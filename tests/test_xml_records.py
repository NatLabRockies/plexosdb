"""The two loading strategies share one raw XML field contract."""

import sqlite3
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from contextlib import closing
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest

from plexosdb import XMLHandler, XMLRecord, element_to_record
from plexosdb.enums import Schema
from plexosdb.solution_reader import PlexosSolution
from plexosdb.solution_reader import xml_parser


@pytest.mark.parametrize("in_memory", [True, False])
def test_shared_fields_and_rename_collisions(tmp_path: Path, in_memory: bool) -> None:
    xml = b"""<MasterDataSet xmlns="http://tempuri.org/MasterDataSet.xsd" xmlns:x="urn:other">
      <t_text><data_id>001</data_id><empty/><space>  </space>
        <value>first</value><x:value>last &amp; &lt;quoted&gt;</x:value>
        <nested>direct<child>not flattened</child>tail</nested></t_text>
      <t_text><data_id>001</data_id><empty/><space>  </space>
        <value>first</value><x:value>last &amp; &lt;quoted&gt;</x:value>
        <nested>direct<child>not flattened</child>tail</nested></t_text>
    </MasterDataSet>"""
    expected = {
        "data_id": "001",
        "empty": None,
        "space": "  ",
        "value": "last & <quoted>",
        "nested": "direct",
    }
    element = ET.fromstring(xml)[0]
    original = ET.tostring(element)
    assert element_to_record(element) == expected
    assert element_to_record(element, rename={"data_id": "value"}) == {
        key: value for key, value in expected.items() if key != "data_id"
    }
    assert ET.tostring(element) == original

    source = tmp_path / "source.xml"
    source.write_bytes(xml)
    handler = XMLHandler.parse(source, in_memory=in_memory)
    assert handler.get_records(Schema.Text) == [expected, expected]
    assert (
        handler.get_records(Schema.Text, rename_dict={"value": "renamed"})
        == [{("renamed" if key == "value" else key): value for key, value in expected.items()}] * 2
    )
    archive = tmp_path / "solution.zip"
    with ZipFile(archive, "w") as zipped:
        zipped.writestr("solution.xml", xml)
    with PlexosSolution.from_zip(archive) as solution:
        solution.to_sqlite(decode_bin_values=False)
        solution.connection.row_factory = sqlite3.Row
        assert [dict(row) for row in solution.connection.execute("SELECT * FROM t_text ORDER BY rowid")] == [
            expected,
            expected,
        ]


@pytest.mark.parametrize("batch_size", [1, 2, 7, 1000])
def test_stream_preserves_order_repeated_rows_and_late_fields(batch_size: int) -> None:
    xml = (
        b"<root>"
        + b"".join(
            b"<t_text>"
            + (b"<value>same</value>" if index < 7 else b"<value/><late>001</late>")
            + f"<ordinal>{index // 2}</ordinal></t_text>".encode()
            + f"<other><ordinal>{index}</ordinal></other>".encode()
            for index in range(15)
        )
        + b"</root>"
    )
    with closing(sqlite3.connect(":memory:")) as connection:
        xml_parser._stream_xml_to_sqlite(connection, BytesIO(xml), batch_size=batch_size)
        assert connection.execute("SELECT value, late, ordinal FROM t_text ORDER BY rowid").fetchall() == [
            ("same", None, str(index // 2)) for index in range(7)
        ] + [(None, "001", str(index // 2)) for index in range(7, 15)]
        assert connection.execute("SELECT ordinal FROM other ORDER BY rowid").fetchall() == [
            (str(index),) for index in range(15)
        ]


def test_stream_batches_before_eof_and_releases_elements(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = b"<root>" + b"<t_text><value>same</value></t_text>" * 3000 + b"</root>"
    source = BytesIO(payload)
    parse = ET.iterparse
    insert = xml_parser._create_and_insert_rows
    batch_lengths: list[int] = []
    positions: list[int] = []
    cleared_rows = 0

    def observe_parse(
        stream: xml_parser._BOMStripStream, *, events: tuple[str, str]
    ) -> Iterator[tuple[str, ET.Element]]:
        nonlocal cleared_rows
        root = None
        depth = 0
        for event, element in parse(stream, events=events):
            if event == "start":
                depth += 1
                if depth == 1:
                    root = element
            yield event, element
            if event == "end":
                if depth == 2:
                    assert root is not None and len(root) == 0
                    assert len(element) == 0 and element.text is None
                    cleared_rows += 1
                depth -= 1

    def observe_insert(connection: sqlite3.Connection, table: str, rows: list[XMLRecord]) -> None:
        batch_lengths.append(len(rows))
        positions.append(source.tell())
        insert(connection, table, rows)

    monkeypatch.setattr(xml_parser.ET, "iterparse", observe_parse)
    monkeypatch.setattr(xml_parser, "_create_and_insert_rows", observe_insert)
    with closing(sqlite3.connect(":memory:")) as connection:
        xml_parser._stream_xml_to_sqlite(connection, source, batch_size=7)
        assert connection.execute("SELECT COUNT(*) FROM t_text").fetchone() == (3000,)
    assert cleared_rows == 3000
    assert max(batch_lengths) == 7
    assert sum(batch_lengths) == 3000
    assert positions[0] < len(payload)


@pytest.mark.parametrize("batch_size", [0, -1])
def test_invalid_batch_size(batch_size: int) -> None:
    with closing(sqlite3.connect(":memory:")) as connection:
        with pytest.raises(ValueError, match="batch_size must be positive"):
            xml_parser._stream_xml_to_sqlite(connection, BytesIO(b"<root/>"), batch_size=batch_size)
