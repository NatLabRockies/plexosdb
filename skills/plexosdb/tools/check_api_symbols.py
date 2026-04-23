#!/usr/bin/env python3
"""Check that key plexosdb symbols still exist at their documented paths.

Intended usage:

    uvx --from python --with plexosdb python scripts/check_api_symbols.py

Exits with non-zero status if any tracked symbol is missing, so this can
be wired into CI after plexosdb version bumps. The symbol list mirrors
the APIs referenced throughout the plexosdb skill documents.
"""

from __future__ import annotations

import importlib
import sys

TRACKED: dict[str, tuple[str, ...]] = {
    "plexosdb": (
        "PlexosDB",
        "PropertyRecord",
        "SQLiteManager",
        "XMLHandler",
        "ClassEnum",
        "CollectionEnum",
    ),
    "plexosdb.db": (
        "PlexosDB",
        "PropertyRecord",
    ),
    "plexosdb.enums": (
        "ClassEnum",
        "CollectionEnum",
    ),
    "plexosdb.xml_handler": ("XMLHandler",),
    "plexosdb.db_manager": ("SQLiteManager",),
}

TRACKED_METHODS: dict[str, tuple[str, ...]] = {
    "plexosdb.db.PlexosDB": (
        "from_xml",
        "to_xml",
        "create_schema",
        "add_object",
        "add_objects",
        "add_membership",
        "add_memberships_from_records",
        "add_property",
        "add_properties_from_records",
        "add_scenario",
        "add_report",
        "add_variable_tag",
        "add_datafile_tag",
        "add_text",
        "copy_object",
        "copy_object_memberships",
        "delete_object",
        "delete_property",
        "delete_membership",
        "get_object_id",
        "get_object_properties",
        "iterate_properties",
        "list_classes",
        "list_collections",
        "list_objects_by_class",
        "list_categories",
        "list_object_memberships",
        "list_parent_objects",
        "list_child_objects",
        "list_scenarios",
        "list_scenarios_by_model",
        "list_models",
        "list_reports",
        "list_valid_properties",
        "list_valid_properties_report",
        "update_property",
        "update_properties",
        "update_object",
        "check_object_exists",
        "check_property_exists",
        "check_membership_exists",
        "get_plexos_version",
        "query",
    ),
}


def _fail(msg: str) -> None:
    print(f"MISSING: {msg}", file=sys.stderr)


def main() -> int:
    failures = 0

    for module_name, names in TRACKED.items():
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001
            _fail(f"import {module_name}: {exc!r}")
            failures += 1
            continue
        for name in names:
            if not hasattr(module, name):
                _fail(f"{module_name}.{name}")
                failures += 1

    for qualname, methods in TRACKED_METHODS.items():
        module_name, _, cls_name = qualname.rpartition(".")
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, cls_name)
        except Exception as exc:  # noqa: BLE001
            _fail(f"import {qualname}: {exc!r}")
            failures += len(methods)
            continue
        for method in methods:
            if not hasattr(cls, method):
                _fail(f"{qualname}.{method}")
                failures += 1

    if failures:
        print(f"FAILED: {failures} symbol(s) missing", file=sys.stderr)
        return 1
    print("OK: all tracked plexosdb symbols present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
