"""DuckDB-style table catalog display helper.

Public surface:
  - :func:`show_db_tables` — print a PLEXOS solution catalog in box format
"""

from __future__ import annotations

from collections.abc import Sequence

from .solution import PlexosSolution

_TABLE_CATALOG_COLUMNS: list[str] = [
    "table_catalog",
    "table_schema",
    "table_name",
    "table_type",
    "self_referencing_column_name",
    "reference_generation",
    "user_defined_type_catalog",
    "user_defined_type_schema",
    "user_defined_type_name",
    "is_insertable_into",
    "is_typed",
    "commit_action",
    "TABLE_COMMENT",
]


def _box_border(widths: list[int], left: str, mid: str, right: str) -> str:
    """Return a horizontal border line using box-drawing characters."""
    return left + mid.join("\u2500" * w for w in widths) + right


def _box_data_line(widths: list[int], vals: Sequence[object], *, center: bool = False) -> str:
    """Return a data row line with values padded to *widths*, bordered by ``│``."""
    parts = []
    for i, v in enumerate(vals):
        s = "NULL" if v is None else str(v)
        pad = widths[i] - 2
        parts.append(f" {s:^{pad}} " if center else f" {s:<{pad}} ")
    return "\u2502" + "\u2502".join(parts) + "\u2502"


def _box_dots_line(widths: list[int]) -> str:
    """Return an ellipsis row (``·``) used when output is truncated."""
    dot = "\u00b7"  # middle dot ·
    return "\u2502" + "\u2502".join(f" {dot:^{w - 2}} " for w in widths) + "\u2502"


def _print_box_table(
    columns: list[str],
    rows: list[tuple[object, ...]],
    *,
    max_rows: int = 20,
) -> None:
    """Print *rows* in DuckDB-style Unicode box format."""
    n = len(rows)
    half = max_rows // 2
    varchar = "varchar"

    widths = [max(len(c), len(varchar)) for c in columns]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len("NULL" if val is None else str(val)))
    widths = [w + 2 for w in widths]

    print(_box_border(widths, "\u250c", "\u252c", "\u2510"))
    print(_box_data_line(widths, columns, center=True))
    print(_box_data_line(widths, [varchar] * len(columns), center=True))
    print(_box_border(widths, "\u251c", "\u253c", "\u2524"))

    if n <= max_rows:
        for row in rows:
            print(_box_data_line(widths, row))
    else:
        for row in rows[:half]:
            print(_box_data_line(widths, row))
        for _ in range(3):
            print(_box_dots_line(widths))
        for row in rows[n - half :]:
            print(_box_data_line(widths, row))

    print(_box_border(widths, "\u2514", "\u2534", "\u2518"))
    shown = min(n, max_rows)
    suffix = f" ({shown} shown)" if n > max_rows else ""
    print(f"  {n} rows{suffix}  {len(columns)} columns")


def show_db_tables(client: PlexosSolution, *, max_rows: int = 20) -> None:
    """Print the table catalog of a PLEXOS solution in DuckDB-style box format.

    Collects all physical tables from attached SQLite schemas together with
    logical derived result tables (``data`` / ``report``) from the solution
    metadata, sorts them by schema then name, and prints the result as a
    Unicode box table — the same visual style used by DuckDB.

    This function must be called after :meth:`PlexosSolution.to_sqlite` has
    been invoked (i.e. after the SQLite connection has been opened).

    Parameters
    ----------
    client
        A :class:`PlexosSolution` instance with an active connection.
    max_rows
        Maximum number of rows to show before truncating with ``·`` rows.
        When the result exceeds *max_rows*, the first and last
        ``max_rows // 2`` rows are displayed.  Defaults to ``20``.

    Examples
    --------
    ::

        from plexosdb import PlexosSolution, show_db_tables

        sol = PlexosSolution.from_zip("my_solution.zip")
        sol.to_sqlite("output.sqlite", if_exists="replace", decode_bin_values=False)

        show_db_tables(sol)
    """
    con = client.connection  # raises RuntimeError if to_sqlite() has not been called
    catalog = client.name
    rows: list[tuple[object, ...]] = []
    seen: set[tuple[str, str]] = set()

    # Physical objects present in all currently attached schemas.
    for _, schema, *_ in con.execute("PRAGMA database_list").fetchall():
        for name, obj_type in con.execute(
            f"SELECT name, type FROM {schema}.sqlite_master WHERE type IN ('table', 'view') ORDER BY name"
        ).fetchall():
            table_type = "BASE TABLE" if obj_type == "table" else "VIEW"
            insertable = "YES" if obj_type == "table" else "NO"
            seen.add((schema, name))
            rows.append(
                (
                    catalog,
                    schema,
                    name,
                    table_type,
                    None,
                    None,
                    None,
                    None,
                    None,
                    insertable,
                    "NO",
                    None,
                    None,
                )
            )

    # Logical derived tables from solution metadata (may not be materialized yet).
    for schema in ("data", "report"):
        ttype = "BASE TABLE" if schema == "data" else "VIEW"
        insertable = "YES" if schema == "data" else "NO"
        for table_info in client.list_tables(schema=schema):
            if (schema, table_info.name) not in seen:
                rows.append(
                    (
                        catalog,
                        schema,
                        table_info.name,
                        ttype,
                        None,
                        None,
                        None,
                        None,
                        None,
                        insertable,
                        "NO",
                        None,
                        None,
                    )
                )

    rows.sort(key=lambda r: (str(r[1]), str(r[2])))
    _print_box_table(_TABLE_CATALOG_COLUMNS, rows, max_rows=max_rows)
