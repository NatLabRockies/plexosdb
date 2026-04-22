"""Model Context Protocol server for plexosdb."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from plexosdb import PlexosDB
from plexosdb.enums import (
    ClassEnum,
    CollectionEnum,
    get_default_collection,
    parse_class_enum,
    parse_collection_enum,
)

try:
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover - exercised only when optional dependency is missing.
    FastMCP = None  # type: ignore[assignment]


class MCPServerState:
    """State manager for active PlexosDB sessions."""

    def __init__(self, *, read_only: bool = False) -> None:
        """Initialize the MCP server state."""
        self._sessions: dict[str, PlexosDB] = {}
        self.read_only = read_only

    @property
    def active_session_count(self) -> int:
        """Return the number of currently active sessions."""
        return len(self._sessions)

    def create_empty_session(self) -> dict[str, Any]:
        """Create a new in-memory PlexosDB session with schema initialized."""
        db = PlexosDB(new_db=True)
        db.create_schema()
        _bootstrap_empty_model(db)

        session_id = str(uuid4())
        self._sessions[session_id] = db
        return {
            "session_id": session_id,
            "version": _serialize_version(db.version),
            "source": "empty",
        }

    def open_xml_session(self, xml_path: str) -> dict[str, Any]:
        """Create a new session by loading an XML model file."""
        db = PlexosDB.from_xml(xml_path=xml_path)

        session_id = str(uuid4())
        self._sessions[session_id] = db
        return {
            "session_id": session_id,
            "version": _serialize_version(db.version),
            "source": str(Path(xml_path)),
        }

    def get_db(self, session_id: str) -> PlexosDB:
        """Resolve and return a session DB handle."""
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            msg = f"Unknown session_id: {session_id}. Create a session first."
            raise ValueError(msg) from exc

    def close_session(self, session_id: str) -> dict[str, Any]:
        """Close and remove a session from memory."""
        db = self.get_db(session_id)
        db._db.close()
        del self._sessions[session_id]
        return {
            "session_id": session_id,
            "closed": True,
        }


def _serialize_version(version: tuple[int, ...] | None) -> list[int] | None:
    """Convert tuple version to JSON-serializable list."""
    if version is None:
        return None
    return list(version)


def _parse_class_name(class_name: str) -> ClassEnum:
    """Parse class enum from user-provided text."""
    try:
        return parse_class_enum(class_name)
    except ValueError as exc:
        msg = f"Invalid class_name '{class_name}'. Use an exact ClassEnum value or member name."
        raise ValueError(msg) from exc


def _parse_collection_name(collection_name: str) -> CollectionEnum:
    """Parse collection enum from user-provided text."""
    try:
        return parse_collection_enum(collection_name)
    except ValueError as exc:
        msg = (
            f"Invalid collection_name '{collection_name}'. Use an exact CollectionEnum value or member name."
        )
        raise ValueError(msg) from exc


def _env_flag(name: str, default: bool = False) -> bool:
    """Read a boolean feature flag from environment variables."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _ensure_writable(server_state: MCPServerState, tool_name: str) -> None:
    """Raise when a write tool is used in read-only mode."""
    if server_state.read_only:
        raise PermissionError(f"Tool '{tool_name}' is disabled in read-only mode")


def _bootstrap_empty_model(db: PlexosDB) -> None:
    """Seed minimal metadata required for object operations in empty sessions."""
    with db._db.transaction():
        class_id_map: dict[ClassEnum, int] = {}
        for idx, class_enum in enumerate(ClassEnum, start=1):
            class_id_map[class_enum] = idx
            db._db.execute(
                "INSERT INTO t_class(class_id, name, description, is_enabled) VALUES (?, ?, ?, ?)",
                (idx, class_enum.value, f"{class_enum.value} class", 1),
            )

        system_class_id = class_id_map[ClassEnum.System]
        db._db.execute(
            "INSERT INTO t_category(category_id, class_id, rank, name) VALUES (?, ?, ?, ?)",
            (1, system_class_id, 1, "-"),
        )
        db._db.execute(
            "INSERT INTO t_object(object_id, class_id, name, category_id, GUID) VALUES (?, ?, ?, ?, ?)",
            (1, system_class_id, "System", 1, str(uuid4())),
        )

        collection_id = 1
        for class_enum in ClassEnum:
            if class_enum is ClassEnum.System:
                continue

            try:
                collection_enum = get_default_collection(class_enum)
            except KeyError:
                # Some classes do not define a default System collection.
                continue

            db._db.execute(
                (
                    "INSERT INTO t_collection("
                    "collection_id, parent_class_id, child_class_id, name, is_enabled"
                    ") "
                    "VALUES (?, ?, ?, ?, ?)"
                ),
                (
                    collection_id,
                    system_class_id,
                    class_id_map[class_enum],
                    collection_enum.value,
                    1,
                ),
            )
            collection_id += 1


def _register_session_tools(mcp: Any, server_state: MCPServerState) -> None:
    """Register session lifecycle tools on the MCP server."""

    @mcp.tool()
    def health() -> dict[str, Any]:
        """Return server status and active session count."""
        return {
            "ok": True,
            "active_sessions": server_state.active_session_count,
            "read_only": server_state.read_only,
        }

    @mcp.tool()
    def create_empty_session() -> dict[str, Any]:
        """Create a new empty PlexosDB session with schema initialized."""
        return server_state.create_empty_session()

    @mcp.tool()
    def open_xml_session(xml_path: str) -> dict[str, Any]:
        """Open a PlexosDB session from a PLEXOS XML file path."""
        return server_state.open_xml_session(xml_path)

    @mcp.tool()
    def close_session(session_id: str) -> dict[str, Any]:
        """Close an existing PlexosDB session and free its resources."""
        return server_state.close_session(session_id)


def _register_object_tools(mcp: Any, server_state: MCPServerState) -> None:
    """Register object and membership discovery tools on the MCP server."""

    @mcp.tool()
    def list_objects_by_class(session_id: str, class_name: str) -> dict[str, Any]:
        """List object names for a class in the target session."""
        db = server_state.get_db(session_id)
        class_enum = _parse_class_name(class_name)
        names = db.list_objects_by_class(class_enum)
        return {
            "session_id": session_id,
            "class_name": class_enum.value,
            "count": len(names),
            "objects": names,
        }

    @mcp.tool()
    def add_object(
        session_id: str,
        class_name: str,
        name: str,
        category: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Add an object to the target session."""
        _ensure_writable(server_state, "add_object")
        db = server_state.get_db(session_id)
        class_enum = _parse_class_name(class_name)

        collection_enum: CollectionEnum | None | bool = None
        try:
            _ = get_default_collection(class_enum)
        except KeyError:
            # Allow classes without a System default collection to be created.
            collection_enum = False

        object_id = db.add_object(
            class_enum,
            name=name,
            category=category,
            description=description,
            collection_enum=collection_enum,
        )
        return {
            "session_id": session_id,
            "object_id": object_id,
            "class_name": class_enum.value,
            "name": name,
        }

    @mcp.tool()
    def add_membership(
        session_id: str,
        parent_class_name: str,
        child_class_name: str,
        parent_name: str,
        child_name: str,
        collection_name: str,
    ) -> dict[str, Any]:
        """Add a membership edge between two objects."""
        _ensure_writable(server_state, "add_membership")
        db = server_state.get_db(session_id)
        parent_class_enum = _parse_class_name(parent_class_name)
        child_class_enum = _parse_class_name(child_class_name)
        collection_enum = _parse_collection_name(collection_name)

        membership_id = db.add_membership(
            parent_class_enum,
            child_class_enum,
            parent_name,
            child_name,
            collection_enum,
        )
        return {
            "session_id": session_id,
            "membership_id": membership_id,
            "collection_name": collection_enum.value,
        }

    @mcp.tool()
    def list_object_memberships(
        session_id: str,
        class_name: str,
        name: str,
        collection_name: str | None = None,
        exclude_system_membership: bool = False,
    ) -> dict[str, Any]:
        """List memberships for a specific object."""
        db = server_state.get_db(session_id)
        class_enum = _parse_class_name(class_name)
        collection = _parse_collection_name(collection_name) if collection_name else None
        memberships = db.list_object_memberships(
            class_enum,
            name=name,
            collection=collection,
            exclude_system_membership=exclude_system_membership,
        )
        return {
            "session_id": session_id,
            "count": len(memberships),
            "memberships": memberships,
        }

    @mcp.tool()
    def list_child_objects(
        session_id: str,
        object_name: str,
        parent_class_name: str,
        child_class_name: str | None = None,
        collection_name: str | None = None,
    ) -> dict[str, Any]:
        """List child objects for a parent object."""
        db = server_state.get_db(session_id)
        parent_class = _parse_class_name(parent_class_name)
        child_class = _parse_class_name(child_class_name) if child_class_name else None
        collection = _parse_collection_name(collection_name) if collection_name else None
        children = db.list_child_objects(
            object_name,
            parent_class=parent_class,
            child_class=child_class,
            collection=collection,
        )
        return {
            "session_id": session_id,
            "count": len(children),
            "children": children,
        }

    @mcp.tool()
    def list_parent_objects(
        session_id: str,
        object_name: str,
        child_class_name: str,
        parent_class_name: str | None = None,
        collection_name: str | None = None,
    ) -> dict[str, Any]:
        """List parent objects for a child object."""
        db = server_state.get_db(session_id)
        child_class = _parse_class_name(child_class_name)
        parent_class = _parse_class_name(parent_class_name) if parent_class_name else None
        collection = _parse_collection_name(collection_name) if collection_name else None
        parents = db.list_parent_objects(
            object_name,
            child_class=child_class,
            parent_class=parent_class,
            collection=collection,
        )
        return {
            "session_id": session_id,
            "count": len(parents),
            "parents": parents,
        }


def _register_edit_tools(mcp: Any, server_state: MCPServerState) -> None:
    """Register model editing tools on the MCP server."""

    @mcp.tool()
    def add_property(
        session_id: str,
        class_name: str,
        object_name: str,
        property_name: str,
        value: str | int | float,
        scenario: str | None = None,
        collection_name: str | None = None,
        parent_class_name: str | None = None,
        parent_object_name: str | None = None,
    ) -> dict[str, Any]:
        """Add a property value for an object in the target session."""
        _ensure_writable(server_state, "add_property")
        db = server_state.get_db(session_id)
        class_enum = _parse_class_name(class_name)
        collection_enum = _parse_collection_name(collection_name) if collection_name else None
        parent_class_enum = _parse_class_name(parent_class_name) if parent_class_name else None

        data_id = db.add_property(
            class_enum,
            object_name,
            property_name,
            value,
            scenario=scenario,
            collection_enum=collection_enum,
            parent_class_enum=parent_class_enum,
            parent_object_name=parent_object_name,
        )
        return {
            "session_id": session_id,
            "data_id": data_id,
            "class_name": class_enum.value,
            "object_name": object_name,
            "property_name": property_name,
        }

    @mcp.tool()
    def add_scenario(session_id: str, name: str, category: str | None = None) -> dict[str, Any]:
        """Add a scenario object to the target session."""
        _ensure_writable(server_state, "add_scenario")
        db = server_state.get_db(session_id)
        scenario_id = db.add_scenario(name, category=category)
        return {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "name": name,
        }

    @mcp.tool()
    def update_object(
        session_id: str,
        class_name: str,
        object_name: str,
        new_name: str,
        new_category: str | None = None,
        new_description: str | None = None,
    ) -> dict[str, Any]:
        """Update object name/category/description."""
        _ensure_writable(server_state, "update_object")
        db = server_state.get_db(session_id)
        class_enum = _parse_class_name(class_name)
        ok = db.update_object(
            class_enum,
            object_name,
            new_name=new_name,
            new_category=new_category,
            new_description=new_description,
        )
        return {
            "session_id": session_id,
            "ok": bool(ok),
            "name": new_name,
        }

    @mcp.tool()
    def delete_object(session_id: str, class_name: str, name: str) -> dict[str, Any]:
        """Delete an object from the target session."""
        _ensure_writable(server_state, "delete_object")
        db = server_state.get_db(session_id)
        class_enum = _parse_class_name(class_name)
        db.delete_object(class_enum, name=name)
        return {
            "session_id": session_id,
            "deleted": True,
            "name": name,
            "class_name": class_enum.value,
        }

    @mcp.tool()
    def delete_property(
        session_id: str,
        class_name: str,
        object_name: str,
        property_name: str,
        collection_name: str | None = None,
        parent_class_name: str | None = None,
        parent_object_name: str | None = None,
        scenario: str | None = None,
    ) -> dict[str, Any]:
        """Delete a property value from an object."""
        _ensure_writable(server_state, "delete_property")
        db = server_state.get_db(session_id)
        class_enum = _parse_class_name(class_name)
        collection = _parse_collection_name(collection_name) if collection_name else None
        parent_class = _parse_class_name(parent_class_name) if parent_class_name else None
        db.delete_property(
            class_enum,
            object_name,
            property_name=property_name,
            collection=collection,
            parent_class=parent_class,
            parent_object_name=parent_object_name,
            scenario=scenario,
        )
        return {
            "session_id": session_id,
            "deleted": True,
            "object_name": object_name,
            "property_name": property_name,
        }

    @mcp.tool()
    def get_object_properties(
        session_id: str,
        class_name: str,
        object_name: str,
        property_names: list[str] | None = None,
    ) -> dict[str, Any]:
        """Return properties for an object in the target session."""
        db = server_state.get_db(session_id)
        class_enum = _parse_class_name(class_name)
        properties = db.get_object_properties(class_enum, object_name, property_names=property_names)
        return {
            "session_id": session_id,
            "class_name": class_enum.value,
            "object_name": object_name,
            "count": len(properties),
            "properties": properties,
        }


def _register_discovery_catalog_tools(mcp: Any, server_state: MCPServerState) -> None:
    """Register catalog/listing discovery tools."""

    @mcp.tool()
    def list_classes(session_id: str) -> dict[str, Any]:
        """List all classes available in the current session model."""
        db = server_state.get_db(session_id)
        classes = db.list_classes()
        return {
            "session_id": session_id,
            "count": len(classes),
            "classes": classes,
        }

    @mcp.tool()
    def list_collections(
        session_id: str,
        parent_class_name: str | None = None,
        child_class_name: str | None = None,
    ) -> dict[str, Any]:
        """List collections, optionally filtered by parent/child class."""
        db = server_state.get_db(session_id)
        parent_class = _parse_class_name(parent_class_name) if parent_class_name else None
        child_class = _parse_class_name(child_class_name) if child_class_name else None
        collections = db.list_collections(parent_class=parent_class, child_class=child_class)
        return {
            "session_id": session_id,
            "count": len(collections),
            "collections": collections,
        }

    @mcp.tool()
    def list_scenarios(session_id: str) -> dict[str, Any]:
        """List scenarios defined in the current session model."""
        db = server_state.get_db(session_id)
        scenarios = db.list_scenarios()
        return {
            "session_id": session_id,
            "count": len(scenarios),
            "scenarios": scenarios,
        }

    @mcp.tool()
    def list_models(session_id: str) -> dict[str, Any]:
        """List models defined in the current session model."""
        db = server_state.get_db(session_id)
        models = db.list_models()
        return {
            "session_id": session_id,
            "count": len(models),
            "models": models,
        }

    @mcp.tool()
    def list_scenarios_by_model(session_id: str, model_name: str) -> dict[str, Any]:
        """List scenarios linked to a specific model."""
        db = server_state.get_db(session_id)
        scenarios = db.list_scenarios_by_model(model_name)
        return {
            "session_id": session_id,
            "model_name": model_name,
            "count": len(scenarios),
            "scenarios": scenarios,
        }

    @mcp.tool()
    def list_valid_properties(
        session_id: str,
        collection_name: str,
        child_class_name: str,
        parent_class_name: str = "System",
    ) -> dict[str, Any]:
        """List valid property names for a collection/parent/child class combination."""
        db = server_state.get_db(session_id)
        collection_enum = _parse_collection_name(collection_name)
        parent_class_enum = _parse_class_name(parent_class_name)
        child_class_enum = _parse_class_name(child_class_name)
        properties = db.list_valid_properties(
            collection_enum,
            parent_class_enum=parent_class_enum,
            child_class_enum=child_class_enum,
        )
        return {
            "session_id": session_id,
            "count": len(properties),
            "properties": properties,
        }

    @mcp.tool()
    def list_reports(session_id: str) -> dict[str, Any]:
        """List report definitions available in the current session model."""
        db = server_state.get_db(session_id)
        try:
            reports = db.list_reports()
        except NotImplementedError:
            reports = []
        return {
            "session_id": session_id,
            "count": len(reports),
            "reports": reports,
        }

    @mcp.tool()
    def list_units(session_id: str) -> dict[str, Any]:
        """List units available in the current session model."""
        db = server_state.get_db(session_id)
        units = db.list_units()
        return {
            "session_id": session_id,
            "count": len(units),
            "units": units,
        }


def _register_discovery_query_tools(mcp: Any, server_state: MCPServerState) -> None:
    """Register query and property discovery tools."""

    @mcp.tool()
    def query_readonly(
        session_id: str,
        sql: str,
        params: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a read-only SQL query (SELECT/CTE) and return rows."""
        statement = sql.lstrip().lower()
        if not (statement.startswith("select") or statement.startswith("with")):
            raise ValueError("query_readonly only allows SELECT/CTE statements")

        db = server_state.get_db(session_id)
        rows = db.query(sql, params=params)
        return {
            "session_id": session_id,
            "count": len(rows),
            "rows": rows,
        }

    @mcp.tool()
    def iterate_properties(
        session_id: str,
        class_name: str | None = None,
        object_names: list[str] | None = None,
        property_names: list[str] | None = None,
        parent_class_name: str | None = None,
        collection_name: str | None = None,
        category: str | None = None,
        batch_size: int = 1000,
        limit: int = 500,
    ) -> dict[str, Any]:
        """Iterate object properties and return up to limit records."""
        db = server_state.get_db(session_id)
        class_enum = _parse_class_name(class_name) if class_name else None
        parent_class = _parse_class_name(parent_class_name) if parent_class_name else None
        collection = _parse_collection_name(collection_name) if collection_name else None

        rows: list[dict[str, Any]] = []
        for idx, row in enumerate(
            db.iterate_properties(
                class_enum=class_enum,
                object_names=object_names,
                property_names=property_names,
                parent_class=parent_class,
                collection=collection,
                category=category,
                batch_size=batch_size,
            )
        ):
            if idx >= limit:
                break
            rows.append(cast(dict[str, Any], row))

        return {
            "session_id": session_id,
            "count": len(rows),
            "rows": rows,
            "limit": limit,
        }


def _register_discovery_tools(mcp: Any, server_state: MCPServerState) -> None:
    """Register discovery and reporting tools on the MCP server."""
    _register_discovery_catalog_tools(mcp, server_state)
    _register_discovery_query_tools(mcp, server_state)


def _register_export_tools(mcp: Any, server_state: MCPServerState) -> None:
    """Register export tools on the MCP server."""

    @mcp.tool()
    def save_xml(session_id: str, output_path: str) -> dict[str, Any]:
        """Export the target session database to a PLEXOS XML file."""
        _ensure_writable(server_state, "save_xml")
        db = server_state.get_db(session_id)
        ok = db.to_xml(output_path)
        return {
            "session_id": session_id,
            "output_path": str(Path(output_path)),
            "ok": bool(ok),
        }

    @mcp.tool()
    def to_csv(session_id: str, output_path: str, tables: list[str] | None = None) -> dict[str, Any]:
        """Export table data to CSV files under output_path."""
        _ensure_writable(server_state, "to_csv")
        db = server_state.get_db(session_id)
        db.to_csv(output_path, tables=tables)
        return {
            "session_id": session_id,
            "output_path": str(Path(output_path)),
            "exported": True,
        }


def _register_admin_tools(mcp: Any, server_state: MCPServerState) -> None:
    """Register administrative and server-introspection tools."""

    @mcp.tool()
    def get_server_config() -> dict[str, Any]:
        """Return server runtime configuration for host diagnostics."""
        return {
            "read_only": server_state.read_only,
            "active_sessions": server_state.active_session_count,
            "categories": {
                "session": ["health", "create_empty_session", "open_xml_session", "close_session"],
                "discovery": [
                    "list_classes",
                    "list_collections",
                    "list_scenarios",
                    "list_models",
                    "list_scenarios_by_model",
                    "list_valid_properties",
                    "list_reports",
                    "list_units",
                    "list_objects_by_class",
                    "list_object_memberships",
                    "list_child_objects",
                    "list_parent_objects",
                    "get_object_properties",
                    "iterate_properties",
                    "query_readonly",
                ],
                "edit": [
                    "add_object",
                    "add_membership",
                    "add_property",
                    "add_scenario",
                    "update_object",
                    "delete_object",
                    "delete_property",
                ],
                "export": ["save_xml", "to_csv"],
                "admin": ["get_server_config"],
            },
        }


def build_mcp_server(state: MCPServerState | None = None, *, read_only: bool | None = None) -> Any:
    """Build and return the MCP server instance."""
    if FastMCP is None:
        msg = "fastmcp is not installed. Install dependencies and run again."
        raise RuntimeError(msg)

    resolved_read_only = read_only if read_only is not None else _env_flag("PLEXOSDB_MCP_READ_ONLY", False)
    if state is None:
        server_state = MCPServerState(read_only=resolved_read_only)
    else:
        state.read_only = resolved_read_only
        server_state = state

    mcp = FastMCP(name="plexosdb")

    _register_session_tools(mcp, server_state)
    _register_object_tools(mcp, server_state)
    _register_edit_tools(mcp, server_state)
    _register_discovery_tools(mcp, server_state)
    _register_export_tools(mcp, server_state)
    _register_admin_tools(mcp, server_state)

    return mcp


def _parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args for the MCP server launcher."""
    parser = argparse.ArgumentParser(description="Run the plexosdb MCP server")
    parser.add_argument(
        "--allow-tty",
        action="store_true",
        help="Allow startup from an interactive terminal (advanced/debug usage).",
    )
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Disable write and export MCP tools for safer production hosts.",
    )
    parser.add_argument(
        "--cli-command",
        choices=["health", "create-empty-session", "open-xml-session"],
        help="Run a one-shot CLI command instead of starting MCP stdio server.",
    )
    parser.add_argument(
        "--xml-path",
        help="Path to XML file used by --cli-command open-xml-session.",
    )
    return parser.parse_args(argv if argv is not None else [])


def _run_cli_command(command: str, xml_path: str | None = None) -> None:
    """Run a one-shot CLI command and print JSON output."""
    state = MCPServerState()

    if command == "health":
        payload = {
            "ok": True,
            "active_sessions": state.active_session_count,
            "mode": "cli",
        }
        print(json.dumps(payload))
        return

    if command == "create-empty-session":
        payload = state.create_empty_session()
        _ = state.close_session(payload["session_id"])
        print(json.dumps(payload))
        return

    if command == "open-xml-session":
        if not xml_path:
            raise ValueError("--xml-path is required for --cli-command open-xml-session")
        payload = state.open_xml_session(xml_path)
        _ = state.close_session(payload["session_id"])
        print(json.dumps(payload))
        return

    raise ValueError(f"Unsupported --cli-command: {command}")


def main(argv: list[str] | None = None) -> None:
    """Run the plexosdb MCP server over stdio."""
    args = _parse_cli_args(argv)

    if args.cli_command:
        _run_cli_command(args.cli_command, xml_path=args.xml_path)
        return

    if sys.stdin.isatty() and not args.allow_tty:
        print("plexosdb-mcp runs over MCP stdio and must be launched by an MCP client.")
        print("Use: npx @modelcontextprotocol/inspector uv run plexosdb-mcp")
        print("Or run with --allow-tty if you intentionally want to keep it running in this terminal.")
        return

    server = build_mcp_server(read_only=args.read_only)
    server.run()


if __name__ == "__main__":
    main(sys.argv[1:])
