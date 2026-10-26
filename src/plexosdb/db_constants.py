"""Shared database configuration and query constants."""

from importlib.resources import files
from string import Template


def get_sql_query(query_name: str) -> str:
    """Load SQL query from package.

    Parameters
    ----------
    query_name : str
        Name of the query file to load from plexosdb.sql

    Returns
    -------
    str
        Content of the SQL query file as a string
    """
    fpath = files("plexosdb.sql").joinpath(query_name)
    return fpath.read_text(encoding="utf-8-sig")


SQLITE_INT64_MIN = -(2**63)
SQLITE_INT64_MAX = 2**63 - 1
SQLITE_ASCII_CASE_FOLD = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
SQLITE_BACKEND_KWARGS = {"in_memory"}
SQLITE_QUERY_CHUNK_SIZE = 900
CHECK_QUERY = "SELECT 1 FROM ${schema} ${where_clause}"
PLEXOS_DEFAULT_SCHEMA = files("plexosdb").joinpath("schema.sql").read_text(encoding="utf-8-sig")
PROPERTY_QUERY = files("plexosdb.sql").joinpath("object_properties.sql").read_text(encoding="utf-8-sig")
MASTER_TEMPLATE_FILES: dict[int, str] = {
    9: "master_9.2R6_btu.xml",
    10: "master_10.0R2_btu.xml",
    11: "master_11.0R4_btu.xml",
    12: "master_12.0R3_btu.xml",
}

MEMBERSHIP_FROM_RECORD_FIELDS = {
    "parent_object_id",
    "child_object_id",
    "collection_id",
    "child_class_id",
    "parent_class_id",
}

SQLITE_INTEGRITY_QUERY = get_sql_query("database_validation_integrity.sql")
FOREIGN_KEY_CHECK_QUERY = get_sql_query("database_validation_foreign_keys.sql")
TABLE_NAMES_QUERY = get_sql_query("database_validation_table_names.sql")
TABLE_INFO_QUERY = Template(get_sql_query("database_validation_table_info.sql"))
RELATIONSHIP_FINDINGS_QUERY = get_sql_query("database_validation_relationships.sql")
CATEGORY_CLASS_FINDINGS_QUERY = get_sql_query("database_validation_category_class.sql")
PROPERTY_COLLECTION_FINDINGS_QUERY = get_sql_query("database_validation_property_collection.sql")
STATIC_PROPERTY_ARTIFACTS_QUERY = Template(get_sql_query("database_validation_static_property_artifacts.sql"))
DUPLICATE_STATIC_DATA_QUERY = get_sql_query("database_validation_duplicate_static_data.sql")
STATIC_DATA_TAGS_QUERY = get_sql_query("database_validation_static_data_tags.sql")
STATIC_DATA_TEXTS_QUERY = get_sql_query("database_validation_static_data_texts.sql")
DATA_GRAPHS_QUERY = get_sql_query("database_validation_data_graphs.sql")
DATA_GRAPH_TAGS_QUERY = get_sql_query("database_validation_data_graph_tags.sql")
DATA_GRAPH_TEXTS_QUERY = get_sql_query("database_validation_data_graph_texts.sql")
DUPLICATE_UIDS_QUERY = get_sql_query("database_validation_duplicate_uids.sql")
ORPHANED_CHILD_ROWS_QUERY = Template(get_sql_query("database_validation_orphaned_child_rows.sql"))
ATTRIBUTE_CLASS_FINDINGS_QUERY = get_sql_query("database_validation_attribute_class.sql")
SYSTEM_MEMBERSHIP_FINDINGS_QUERY = get_sql_query("database_validation_system_membership.sql")
MEMBERSHIP_COUNT_BOUNDS_QUERY = get_sql_query("database_validation_membership_count_bounds.sql")
VALID_TAG_CLASS_LANG_IDS = (29, 31, 34, 35)  # Data File, Variable, Timeslice, Scenario
TAG_OBJECT_CLASS_QUERY = Template(get_sql_query("database_validation_tag_object_class.sql")).substitute(
    placeholders=",".join("?" * len(VALID_TAG_CLASS_LANG_IDS))
)
VARIABLE_CLASS_LANG_ID = 31
ACTION_TAG_FINDINGS_QUERY = get_sql_query("database_validation_action_tags.sql")
ACTION_TEXT_FINDINGS_QUERY = get_sql_query("database_validation_action_texts.sql")
BAND_COUNT_FINDINGS_QUERY = get_sql_query("database_validation_band_count.sql")
PROPERTY_VALUES_QUERY = get_sql_query("database_validation_property_values.sql")
ATTRIBUTE_VALUES_QUERY = get_sql_query("database_validation_attribute_values.sql")
NAME_COLLISIONS_QUERY = get_sql_query("database_validation_name_collisions.sql")
CUSTOM_COLUMN_CLASS_QUERY = get_sql_query("database_validation_custom_column_class.sql")
SIMULATION_ATTRIBUTE_RULE_OVERRIDES = {
    ("Transmission", "Loss Tolerance"): ">=0",
    ("Transmission", "Flow PTDF Threshold"): ">=0",
    ("Production", "Fuel Use Function Precision"): ">=0",
    ("Production", "Rounding Up Threshold"): "Between 0 And 1",
    ("Performance", "MIP Relative Gap"): ">=0",
}
INTEGER_ATTRIBUTE_EXEMPTIONS = frozenset(
    (*SIMULATION_ATTRIBUTE_RULE_OVERRIDES, ("Transmission", "Loss Function Precision"))
)
REPAIR_MEMBERSHIP_CLASS_IDS_SCRIPT = get_sql_query("database_validation_repair_memberships.sql")
