from __future__ import annotations

import json
import pytest

from plexosdb import ClassEnum
from plexosdb.enums import CollectionEnum
from plexosdb.mcp_server import MCPServerState
import plexosdb.mcp_server as mcp_server


class FakeFastMCP:
    """Minimal FastMCP stand-in for unit testing tool registration."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.tools: dict[str, object] = {}
        self.ran = False

    def tool(self):
        """Return decorator that registers a function by name."""

        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator

    def run(self) -> None:
        """Record that run was called."""
        self.ran = True


class FakeDB:
    """Simple DB facade used by tool-level MCP tests."""

    def __init__(self) -> None:
        self.saved_path: str | None = None
        self.last_add_object: dict[str, object] | None = None
        self.last_add_property: dict[str, object] | None = None
        self.last_query_sql: str | None = None

    def list_objects_by_class(self, class_enum: ClassEnum) -> list[str]:
        """Return deterministic object names for a class."""
        return [f"{class_enum.value}-A", f"{class_enum.value}-B"]

    def add_object(
        self,
        class_enum: ClassEnum,
        /,
        name: str,
        *,
        description: str | None = None,
        category: str | None = None,
        collection_enum: CollectionEnum | None | bool = None,
    ) -> int:
        """Capture add_object inputs and return a stable object id."""
        self.last_add_object = {
            "class_enum": class_enum,
            "name": name,
            "description": description,
            "category": category,
            "collection_enum": collection_enum,
        }
        return 101

    def add_membership(
        self,
        parent_class_enum: ClassEnum,
        child_class_enum: ClassEnum,
        parent_object_name: str,
        child_object_name: str,
        collection_enum: CollectionEnum,
    ) -> int:
        """Validate membership inputs and return a stable membership id."""
        assert parent_class_enum is ClassEnum.Generator
        assert child_class_enum is ClassEnum.Node
        assert parent_object_name == "Gen-1"
        assert child_object_name == "Node-1"
        assert collection_enum is CollectionEnum.Nodes
        return 202

    def add_property(
        self,
        object_class_enum: ClassEnum,
        /,
        object_name: str,
        name: str,
        value: str | int | float,
        *,
        scenario: str | None = None,
        collection_enum: CollectionEnum | None = None,
        parent_class_enum: ClassEnum | None = None,
        parent_object_name: str | None = None,
    ) -> int:
        """Capture add_property inputs and return a stable data id."""
        self.last_add_property = {
            "object_class_enum": object_class_enum,
            "object_name": object_name,
            "name": name,
            "value": value,
            "scenario": scenario,
            "collection_enum": collection_enum,
            "parent_class_enum": parent_class_enum,
            "parent_object_name": parent_object_name,
        }
        return 303

    def get_object_properties(
        self,
        class_enum: ClassEnum,
        /,
        name: str,
        property_names: list[str] | None = None,
    ) -> list[dict[str, object]]:
        """Return a deterministic property payload."""
        return [
            {
                "class": class_enum.value,
                "name": name,
                "property_names": property_names,
            }
        ]

    def to_xml(self, target_path: str) -> bool:
        """Capture output path and simulate successful export."""
        self.saved_path = target_path
        return True

    def list_classes(self) -> list[str]:
        """Return deterministic class names."""
        return ["System", "Generator", "Node"]

    def list_collections(
        self,
        /,
        *,
        parent_class: ClassEnum | None = None,
        child_class: ClassEnum | None = None,
    ) -> list[dict[str, object]]:
        """Return deterministic collection records."""
        return [
            {
                "name": "Generators",
                "parent": (parent_class or ClassEnum.System).value,
                "child": (child_class or ClassEnum.Generator).value,
            }
        ]

    def list_scenarios(self) -> list[str]:
        """Return deterministic scenarios."""
        return ["Base", "High"]

    def list_valid_properties(
        self,
        collection_enum: CollectionEnum,
        /,
        parent_class_enum: ClassEnum,
        child_class_enum: ClassEnum,
    ) -> list[str]:
        """Return deterministic valid property names."""
        assert collection_enum is CollectionEnum.Generators
        assert parent_class_enum is ClassEnum.System
        assert child_class_enum is ClassEnum.Generator
        return ["Max Capacity", "Min Stable Level"]

    def list_reports(self) -> list[dict[str, object]]:
        """Return deterministic report metadata."""
        return [{"name": "Summary", "enabled": 1}]

    def list_units(self) -> list[dict[int, str]]:
        """Return deterministic unit metadata."""
        return [{1: "MW"}]

    def query(
        self,
        query_string: str,
        params: tuple[object, ...] | dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        """Capture query and return deterministic rows."""
        self.last_query_sql = query_string
        return [{"row": 1, "params": params}]


class FakeState:
    """State object for exercising all registered tools."""

    def __init__(self) -> None:
        self.db = FakeDB()

    @property
    def active_session_count(self) -> int:
        """Return a deterministic active session count."""
        return 7

    def create_empty_session(self) -> dict[str, object]:
        """Return a deterministic create-session response."""
        return {"session_id": "s-empty", "version": [10, 0], "source": "empty"}

    def open_xml_session(self, xml_path: str) -> dict[str, object]:
        """Return a deterministic open-session response."""
        return {"session_id": "s-xml", "version": [10, 0], "source": xml_path}

    def close_session(self, session_id: str) -> dict[str, object]:
        """Return a deterministic close-session response."""
        return {"session_id": session_id, "closed": True}

    def get_db(self, session_id: str) -> FakeDB:
        """Return the fake DB for the expected session id."""
        assert session_id == "sid"
        return self.db


class StubStdin:
    """Stub stdin with configurable TTY behavior."""

    def __init__(self, is_tty: bool) -> None:
        self._is_tty = is_tty

    def isatty(self) -> bool:
        """Return configured TTY behavior."""
        return self._is_tty


def test_create_empty_session_and_close() -> None:
    state = MCPServerState()

    created = state.create_empty_session()
    session_id = created["session_id"]

    assert isinstance(session_id, str)
    assert state.active_session_count == 1

    db = state.get_db(session_id)
    assert db.check_class_exists(ClassEnum.Generator)
    assert "System" in db.list_objects_by_class(ClassEnum.System)

    object_id = db.add_object(ClassEnum.Generator, name="Gen-MCP")
    assert isinstance(object_id, int)

    objects = db.list_objects_by_class(ClassEnum.Generator)
    assert "Gen-MCP" in objects

    closed = state.close_session(session_id)
    assert closed == {"session_id": session_id, "closed": True}
    assert state.active_session_count == 0


def test_open_xml_session_and_invalid_session(data_folder) -> None:
    state = MCPServerState()
    xml_path = data_folder / "plexosdb.xml"

    created = state.open_xml_session(str(xml_path))
    session_id = created["session_id"]

    assert isinstance(session_id, str)
    assert created["source"].endswith("plexosdb.xml")

    db = state.get_db(session_id)
    generators = db.list_objects_by_class(ClassEnum.Generator)
    assert isinstance(generators, list)

    with pytest.raises(ValueError, match="Unknown session_id"):
        _ = state.get_db("missing-session")

    _ = state.close_session(session_id)


def test_build_mcp_server_raises_without_fastmcp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mcp_server, "FastMCP", None)

    with pytest.raises(RuntimeError, match="fastmcp is not installed"):
        _ = mcp_server.build_mcp_server()


def test_build_mcp_server_registers_and_runs_all_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mcp_server, "FastMCP", FakeFastMCP)
    state = FakeState()

    mcp = mcp_server.build_mcp_server(state)
    assert mcp.name == "plexosdb"

    health = mcp.tools["health"]()
    assert health == {"ok": True, "active_sessions": 7}

    created = mcp.tools["create_empty_session"]()
    assert created["session_id"] == "s-empty"

    opened = mcp.tools["open_xml_session"]("/tmp/model.xml")
    assert opened["session_id"] == "s-xml"

    listed = mcp.tools["list_objects_by_class"]("sid", "Generator")
    assert listed["count"] == 2

    added_obj = mcp.tools["add_object"]("sid", "Generator", "Gen-1", category="Thermal")
    assert added_obj["object_id"] == 101
    assert state.db.last_add_object
    assert state.db.last_add_object["collection_enum"] is None

    # Timeslice has no default collection enum, so the tool forces collection_enum=False.
    _ = mcp.tools["add_object"]("sid", "Timeslice", "TS-1")
    assert state.db.last_add_object
    assert state.db.last_add_object["collection_enum"] is False

    added_membership = mcp.tools["add_membership"](
        "sid",
        "Generator",
        "Node",
        "Gen-1",
        "Node-1",
        "Nodes",
    )
    assert added_membership["membership_id"] == 202

    added_prop = mcp.tools["add_property"](
        "sid",
        "Generator",
        "Gen-1",
        "Max Capacity",
        123.0,
        scenario="Base",
        collection_name="Generators",
        parent_class_name="System",
        parent_object_name="System",
    )
    assert added_prop["data_id"] == 303
    assert state.db.last_add_property
    assert state.db.last_add_property["collection_enum"] is CollectionEnum.Generators
    assert state.db.last_add_property["parent_class_enum"] is ClassEnum.System

    props = mcp.tools["get_object_properties"](
        "sid",
        "Generator",
        "Gen-1",
        property_names=["Max Capacity"],
    )
    assert props["count"] == 1

    saved = mcp.tools["save_xml"]("sid", "/tmp/out.xml")
    assert saved["ok"] is True
    assert state.db.saved_path == "/tmp/out.xml"

    classes = mcp.tools["list_classes"]("sid")
    assert classes["count"] == 3

    collections = mcp.tools["list_collections"]("sid", "System", "Generator")
    assert collections["count"] == 1

    scenarios = mcp.tools["list_scenarios"]("sid")
    assert scenarios["count"] == 2

    valid_props = mcp.tools["list_valid_properties"]("sid", "Generators", "Generator")
    assert valid_props["count"] == 2

    reports = mcp.tools["list_reports"]("sid")
    assert reports["count"] == 1

    units = mcp.tools["list_units"]("sid")
    assert units["count"] == 1

    rows = mcp.tools["query_readonly"]("sid", "SELECT 1")
    assert rows["count"] == 1
    assert state.db.last_query_sql == "SELECT 1"

    closed = mcp.tools["close_session"]("sid")
    assert closed["closed"] is True


def test_tool_input_validation_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mcp_server, "FastMCP", FakeFastMCP)
    state = FakeState()
    mcp = mcp_server.build_mcp_server(state)

    with pytest.raises(ValueError, match="Invalid class_name"):
        _ = mcp.tools["list_objects_by_class"]("sid", "NotAClass")

    with pytest.raises(ValueError, match="Invalid collection_name"):
        _ = mcp.tools["add_membership"]("sid", "Generator", "Node", "A", "B", "NotACollection")

    with pytest.raises(ValueError, match="only allows SELECT/CTE"):
        _ = mcp.tools["query_readonly"]("sid", "DELETE FROM t_object")


def test_main_prints_hint_when_launched_interactively(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(mcp_server.sys, "stdin", StubStdin(True))

    mcp_server.main()
    captured = capsys.readouterr().out

    assert "must be launched by an MCP client" in captured
    assert "@modelcontextprotocol/inspector" in captured


def test_main_runs_server_when_not_interactive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mcp_server.sys, "stdin", StubStdin(False))
    fake_mcp = FakeFastMCP(name="plexosdb")
    monkeypatch.setattr(mcp_server, "build_mcp_server", lambda: fake_mcp)

    mcp_server.main()

    assert fake_mcp.ran is True


def test_main_runs_server_with_allow_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mcp_server.sys, "stdin", StubStdin(True))
    fake_mcp = FakeFastMCP(name="plexosdb")
    monkeypatch.setattr(mcp_server, "build_mcp_server", lambda: fake_mcp)

    mcp_server.main(["--allow-tty"])

    assert fake_mcp.ran is True


def test_main_cli_health_outputs_json(capsys: pytest.CaptureFixture[str]) -> None:
    mcp_server.main(["--cli-command", "health"])
    out = capsys.readouterr().out.strip()

    payload = json.loads(out)
    assert payload["ok"] is True
    assert payload["mode"] == "cli"


def test_main_cli_create_empty_session_outputs_json(capsys: pytest.CaptureFixture[str]) -> None:
    mcp_server.main(["--cli-command", "create-empty-session"])
    out = capsys.readouterr().out.strip()

    payload = json.loads(out)
    assert payload["source"] == "empty"
    assert isinstance(payload["session_id"], str)


def test_main_cli_open_xml_session_outputs_json(
    capsys: pytest.CaptureFixture[str],
    data_folder,
) -> None:
    xml_path = data_folder / "plexosdb.xml"

    mcp_server.main(["--cli-command", "open-xml-session", "--xml-path", str(xml_path)])
    out = capsys.readouterr().out.strip()

    payload = json.loads(out)
    assert payload["source"].endswith("plexosdb.xml")
    assert isinstance(payload["session_id"], str)


def test_main_cli_open_xml_session_requires_path() -> None:
    with pytest.raises(ValueError, match="--xml-path is required"):
        mcp_server.main(["--cli-command", "open-xml-session"])
