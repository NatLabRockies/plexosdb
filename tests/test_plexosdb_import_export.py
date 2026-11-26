from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from plexosdb import PlexosDB


def _create_csv_test_schema(db: PlexosDB) -> None:
    db._db.execute("""
        CREATE TABLE z_parent (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    db._db.execute("""
        CREATE TABLE a_child (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER REFERENCES z_parent(id),
            note TEXT,
            payload BLOB
        )
    """)


def test_backup_database_copies_in_memory_database(tmp_path: Path) -> None:
    db = PlexosDB()
    try:
        db._db.execute("CREATE TABLE sample (value TEXT)")
        db._db.execute("INSERT INTO sample VALUES (?)", ("backup value",))

        backup_path = tmp_path / "nested" / "backup.sqlite"
        db.backup_database(backup_path)

        with sqlite3.connect(backup_path) as backup:
            assert backup.execute("SELECT value FROM sample").fetchone() == ("backup value",)
    finally:
        db._db.close()


def test_backup_database_rejects_source_as_target(tmp_path: Path) -> None:
    database_path = tmp_path / "source.sqlite"
    db = PlexosDB(database_path)
    try:
        with pytest.raises(ValueError, match="must differ"):
            db.backup_database(database_path)
    finally:
        db._db.close()


def test_csv_round_trip_preserves_nulls_strings_blobs_and_foreign_keys(tmp_path: Path) -> None:
    source_db = PlexosDB()
    target_db = PlexosDB()
    try:
        _create_csv_test_schema(source_db)
        _create_csv_test_schema(target_db)
        source_db._db.execute("INSERT INTO z_parent VALUES (?, ?)", (1, "parent"))
        source_db._db.execute(
            "INSERT INTO a_child VALUES (?, ?, ?, ?)",
            (1, 1, "first,\nsecond", b"\x00\xff"),
        )
        source_db._db.execute("INSERT INTO a_child VALUES (?, ?, ?, ?)", (2, 1, r"\N", None))
        source_db._db.execute("INSERT INTO a_child VALUES (?, ?, ?, ?)", (3, 1, "", b""))

        export_path = tmp_path / "csv"
        source_db.to_csv(export_path)
        target_db.import_from_csv(export_path)

        rows = target_db._db.connection.execute(
            "SELECT id, parent_id, note, payload FROM a_child ORDER BY id"
        ).fetchall()
        assert [tuple(row) for row in rows] == [
            (1, 1, "first,\nsecond", b"\x00\xff"),
            (2, 1, r"\N", None),
            (3, 1, "", b""),
        ]
        assert target_db._db.connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        source_db._db.close()
        target_db._db.close()


def test_csv_export_selection_and_single_file_import(tmp_path: Path) -> None:
    source_db = PlexosDB()
    target_db = PlexosDB()
    try:
        _create_csv_test_schema(source_db)
        target_db._db.execute("CREATE TABLE z_parent (id INTEGER PRIMARY KEY, name TEXT)")
        source_db._db.execute("INSERT INTO z_parent VALUES (?, ?)", (1, "selected"))

        export_path = tmp_path / "selected"
        source_db.to_csv(export_path, tables=["z_parent"])

        assert [path.name for path in export_path.iterdir()] == ["z_parent.csv"]
        target_db.import_from_csv(export_path / "z_parent.csv")
        rows = target_db._db.connection.execute("SELECT * FROM z_parent").fetchall()
        assert [tuple(row) for row in rows] == [(1, "selected")]
    finally:
        source_db._db.close()
        target_db._db.close()


def test_import_from_csv_rolls_back_all_rows_on_constraint_failure(tmp_path: Path) -> None:
    db = PlexosDB()
    try:
        db._db.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT)")
        csv_path = tmp_path / "sample.csv"
        csv_path.write_text("id,value\n1,first\n1,duplicate\n", encoding="utf-8")

        with pytest.raises(sqlite3.IntegrityError):
            db.import_from_csv(csv_path)

        assert db._db.connection.execute("SELECT * FROM sample").fetchall() == []
    finally:
        db._db.close()
