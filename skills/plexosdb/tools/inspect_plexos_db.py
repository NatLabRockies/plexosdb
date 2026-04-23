#!/usr/bin/env python3
"""Inspect a plexosdb SQLite projection: table counts and sample rows.

Usage:

    uvx --from python python scripts/inspect_plexos_db.py <path/to/db.sqlite> \
        [--sample N] [--tables t_object t_property ...]

Prints row counts for every table, then an optional sample of N rows
for each table (or just the tables passed via --tables).

The script intentionally uses only the standard library so it can run
without plexosdb installed, which is useful when debugging a database
file produced by a different plexosdb version.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("db_path", type=Path)
    parser.add_argument("--sample", type=int, default=0, help="Rows per table")
    parser.add_argument(
        "--tables",
        nargs="*",
        default=None,
        help="Restrict inspection to these tables",
    )
    return parser.parse_args(argv)


def _list_tables(cur: sqlite3.Cursor) -> list[str]:
    cur.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    )
    return [row[0] for row in cur.fetchall()]


def _count(cur: sqlite3.Cursor, table: str) -> int:
    cur.execute(f'SELECT COUNT(*) FROM "{table}"')
    return int(cur.fetchone()[0])


def _sample(cur: sqlite3.Cursor, table: str, n: int) -> list[tuple[tuple[str, ...], list[tuple]]]:
    cur.execute(f'SELECT * FROM "{table}" LIMIT ?', (n,))
    cols = tuple(desc[0] for desc in (cur.description or ()))
    return [(cols, cur.fetchall())]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if not args.db_path.is_file():
        print(f"FAIL: not a file: {args.db_path}", file=sys.stderr)
        return 1

    with sqlite3.connect(f"file:{args.db_path}?mode=ro", uri=True) as conn:
        cur = conn.cursor()
        tables = _list_tables(cur)
        if args.tables is not None:
            tables = [t for t in tables if t in set(args.tables)]

        print(f"# plexosdb SQLite inspection: {args.db_path}")
        print(f"# tables: {len(tables)}")
        for table in tables:
            count = _count(cur, table)
            print(f"{table}\t{count}")

        if args.sample > 0:
            for table in tables:
                print(f"\n## sample: {table}")
                for cols, rows in _sample(cur, table, args.sample):
                    if not rows:
                        print("(empty)")
                        continue
                    print("\t".join(cols))
                    for row in rows:
                        print("\t".join("" if v is None else str(v) for v in row))

    return 0


if __name__ == "__main__":
    sys.exit(main())
