"""Public facade for plexosdb solution reader.

Import ``PlexosSolution`` from here.
All private helpers are re-exported so that existing
``from plexosdb.solution_reader import _foo`` call-sites (e.g. tests)
continue to work without change.
"""

from __future__ import annotations

from .archive import _resolve_input_zip_path, _select_xml_entry
from .bin_decoder import (
    _bin_entry_name_map,
    _decode_bin_values,
    _decode_period_rows,
    _group_key_rows_by_period,
    _read_all_bin_entries,
    _skip_bytes,
)
from .materialize import (
    _PERIOD_TABLE_META,
    _attach_solution_schemas,
    _attached_db_names,
    _build_derived_table_map,
    _build_fallback_create_sql,
    _build_key_period_map,
    _build_period_join,
    _build_phase_sets,
    _build_property_map,
    _build_rich_create_sql,
    _copy_data_table_to_report,
    _ensure_join_indexes,
    _materialize_single_solution_table,
    _materialize_single_solution_table_from_subset,
    _materialize_solution_tables,
    _period_type_name,
    _phase_name,
    _report_interval_length,
    _resolve_report_unit,
    _sanitize_name,
    _table_columns,
    _table_label_part,
)
from .display import show_db_tables
from .solution import PlexosSolution
from .types import MaterializeResult, SolutionInfo, SQLiteResult, TableInfo
from .utils import _coerce_value, _local_name, _quote_ident
from .xml_parser import _BOMStripStream, _create_and_insert_rows, _stream_xml_to_sqlite

__all__ = [
    "MaterializeResult",
    "PlexosSolution",
    "SQLiteResult",
    "SolutionInfo",
    "TableInfo",
]
