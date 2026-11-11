import ast
from pathlib import Path
import runpy

import pytest


@pytest.fixture(scope="module")
def api_generator():
    script = Path(__file__).resolve().parents[1] / "docs" / "generate_api.py"
    return runpy.run_path(str(script))


@pytest.mark.parametrize("member_name", ("add_property", "__init__"))
def test_api_reference_preserves_docstrings(api_generator, member_name):
    path, node = api_generator["root_export_definitions"]()["PlexosDB"]
    member = next(
        child for child in node.body if isinstance(child, ast.FunctionDef) and child.name == member_name
    )
    content, _ = api_generator["render_object"]("PlexosDB", path, node, "test")

    documentation = api_generator["render_docstring"](member)
    assert documentation in content
    summary, _, details = ast.get_docstring(member).partition("\n\n")
    assert summary in documentation
    for line in details.splitlines():
        if line.strip() and set(line.strip()) != {"-"}:
            assert line.strip().replace("`", "") in documentation.replace("`", "")
    assert "**Parameters**" in content
    assert "```text\nParameters" not in content


def test_api_docstring_sections_render_as_markdown(api_generator):
    _, node = api_generator["root_export_definitions"]()["PlexosDB"]
    member = next(
        child for child in node.body if isinstance(child, ast.FunctionDef) and child.name == "add_property"
    )
    content = api_generator["render_docstring"](member)

    assert "**Parameters**\n\n- `object_class_enum : ClassEnum`\n  Class enumeration of the object" in content
    assert "**Returns**\n\n- `int`\n  ID of the created property data record" in content
    assert "**Examples**\n\n```python\n>>> db = PlexosDB()" in content


@pytest.mark.parametrize(
    ("module", "has_root_reference"),
    (("plexosdb.db_solution", True), ("plexosdb.solution_reader.solution", False)),
)
def test_module_reference_uses_export_definition(api_generator, module, has_root_reference):
    roots = api_generator["root_export_definitions"]()
    exported = {(path, api_generator["definition_name"](node)): name for name, (path, node) in roots.items()}
    path = api_generator["module_source"](module)
    node = api_generator["source_definition"](ast.parse(path.read_text()), "PlexosSolution")
    lines = api_generator["render_module_definition"](module, path, node, "test", exported, "/reference/", {})

    link = "Full reference: [`PlexosSolution`](/plexosdb/reference/python-api/plexossolution/)."
    assert (link in "\n".join(lines)) is has_root_reference


def test_api_properties_are_not_callable(api_generator):
    path, node = api_generator["root_export_definitions"]()["PlexosDB"]
    content, _ = api_generator["render_object"]("PlexosDB", path, node, "test")
    lines = api_generator["render_module_definition"](
        "plexosdb.db", path, node, "test", {}, "/reference/", {}
    )

    for reference in (content, "\n".join(lines)):
        assert "version: tuple[int, ...] | None" in reference
        assert "\nversion(self)" not in reference
        assert "add_property(self," in reference
