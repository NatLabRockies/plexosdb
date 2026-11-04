"""Generate API pages and navigation from PLEXOSDB's Python source."""

from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = Path(__file__).resolve().parent
SOURCE = ROOT / "src/plexosdb"
PAGES = DOCS / "src/content/docs/reference/python-api"
MODULE_PAGES = DOCS / "src/content/docs/reference/api/modules"
NAVIGATION = DOCS / "src/generated/api-sidebar.json"
FRAGMENTS = DOCS / "public/api-fragments.json"
MODULES = {
    "checks": ("plexosdb.checks",),
    "db_solution": ("plexosdb.db_solution", "plexosdb.db_solution_models"),
    "enums": ("plexosdb.enums",),
    "exceptions": ("plexosdb.exceptions",),
    "plexosdb": ("plexosdb.db",),
    "solution_reader": (
        "plexosdb.solution_reader.solution",
        "plexosdb.solution_reader.display",
        "plexosdb.solution_reader.types",
    ),
    "sqlite_manager": ("plexosdb.db_manager",),
    "utils": ("plexosdb.utils",),
    "xml_handler": ("plexosdb.xml_handler",),
}
MODULE_LABELS = {
    "checks": "Checks",
    "db_solution": "DuckDB solution",
    "enums": "Enumerations",
    "exceptions": "Exceptions",
    "plexosdb": "PlexosDB",
    "solution_reader": "SQLite solution reader",
    "sqlite_manager": "SQLite manager",
    "utils": "Utilities",
    "xml_handler": "XML handler",
}
GENERATED_START = "<!-- Generated API reference -->"
GENERATED_END = "<!-- End generated API reference -->"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def anchor(name: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", name.lower()).strip("-")


def public_names() -> list[str]:
    module = ast.parse((SOURCE / "__init__.py").read_text())
    assignment = next(
        node.value
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
    )
    return [name for name in ast.literal_eval(assignment) if not name.startswith("_")]


def definition_name(node: ast.AST) -> str | None:
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return node.name
    if isinstance(node, ast.Assign):
        return next((target.id for target in node.targets if isinstance(target, ast.Name)), None)
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    return None


def source_definition(module: ast.Module, name: str) -> ast.AST | None:
    return next((node for node in module.body if definition_name(node) == name), None)


def import_source_path(node: ast.ImportFrom) -> Path:
    module_path = SOURCE.joinpath(*(node.module or "").split("."))
    source_path = module_path.with_suffix(".py")
    return source_path if source_path.is_file() else module_path / "__init__.py"


def root_export_definitions() -> dict[str, tuple[Path, ast.AST]]:
    root = ast.parse((SOURCE / "__init__.py").read_text())
    names = set(public_names())
    result: dict[str, tuple[Path, ast.AST]] = {}
    for imported_from in root.body:
        if not isinstance(imported_from, ast.ImportFrom) or imported_from.level == 0:
            continue
        source_path = import_source_path(imported_from)
        module = ast.parse(source_path.read_text())
        for imported in imported_from.names:
            export_name = imported.asname or imported.name
            if export_name in names and (definition := source_definition(module, imported.name)):
                result[export_name] = (source_path, definition)
    missing = names - result.keys()
    if missing:
        raise KeyError(f"Could not resolve root exports to source: {sorted(missing)}")
    return result


def doc_summary(node: ast.AST) -> str:
    if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""
    doc = ast.get_docstring(node)
    return doc.split("\n\n", 1)[0].strip() if doc else ""


def source_url(path: Path, node: ast.AST, revision: str) -> str:
    relative = path.relative_to(ROOT)
    return f"https://github.com/NatLabRockies/plexosdb/blob/{revision}/{relative}#L{node.lineno}"


def function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    result = ast.unparse(node.returns) if node.returns else "unspecified"
    return f"{node.name}({ast.unparse(node.args)}) -> {result}"


def class_methods(node: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        child
        for child in node.body
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and not child.name.startswith("_")
    ]


def render_class_fields(node: ast.ClassDef, route: str) -> tuple[list[str], list[dict[str, str]]]:
    lines: list[str] = []
    members: list[dict[str, str]] = []
    fields = [child for child in node.body if isinstance(child, ast.AnnAssign)]
    if fields:
        lines.append("## Declared fields\n")
    for field in fields:
        field_name = ast.unparse(field.target)
        lines += [f"### {field_name}\n", f"```text\n{ast.unparse(field)}\n```\n"]
        members.append({"label": field_name, "link": route + "#" + anchor(field_name)})
    return lines, members


def is_enum_class(node: ast.ClassDef) -> bool:
    enum_bases = {"Enum", "StrEnum", "IntEnum", "Flag", "IntFlag"}
    return any(ast.unparse(base).rsplit(".", 1)[-1] in enum_bases for base in node.bases)


def render_enum_values(node: ast.ClassDef, route: str) -> tuple[list[str], list[dict[str, str]]]:
    lines: list[str] = []
    members: list[dict[str, str]] = []
    values = [
        child
        for child in node.body
        if isinstance(child, ast.Assign)
        and is_enum_class(node)
        and any(isinstance(target, ast.Name) and not target.id.startswith("_") for target in child.targets)
    ]
    if values:
        lines.append("## Enum values\n")
    for value in values:
        for target in value.targets:
            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                lines += [f"### {target.id}\n", f"```text\n{ast.unparse(value)}\n```\n"]
                members.append({"label": target.id, "link": route + "#" + anchor(target.id)})
    return lines, members


def render_class_methods(
    node: ast.ClassDef,
    path: Path,
    route: str,
    revision: str,
) -> tuple[list[str], list[dict[str, str]]]:
    lines = ["## Declared methods\n"]
    members: list[dict[str, str]] = []
    for method in class_methods(node):
        lines += [
            f"### {method.name}\n",
            f"[Source]({source_url(path, method, revision)})\n",
            f"```text\n{function_signature(method)}\n```\n",
        ]
        if summary := doc_summary(method):
            lines.append(summary + "\n")
        members.append({"label": method.name, "link": route + "#" + anchor(method.name)})
    return lines, members


def render_class(
    node: ast.ClassDef,
    path: Path,
    route: str,
    revision: str,
) -> tuple[list[str], list[dict[str, str]]]:
    lines, members = render_class_fields(node, route)
    enum_lines, enum_members = render_enum_values(node, route)
    lines.extend(enum_lines)
    members.extend(enum_members)
    constructor = next(
        (child for child in node.body if isinstance(child, ast.FunctionDef) and child.name == "__init__"),
        None,
    )
    if constructor:
        lines += ["## Constructor\n", f"```text\n{function_signature(constructor)}\n```\n"]
    method_lines, method_members = render_class_methods(node, path, route, revision)
    lines.extend(method_lines)
    members.extend(method_members)
    return lines, members


def render_object(name: str, path: Path, node: ast.AST, revision: str) -> tuple[str, list[dict[str, str]]]:
    route = f"/reference/python-api/{slug(name)}/"
    members: list[dict[str, str]] = [{"label": name, "link": route}]
    lines = [
        f"---\ntitle: {json.dumps(name)}\neditUrl: false\n---\n",
        f"[Source]({source_url(path, node, revision)})\n",
    ]
    summary = doc_summary(node)
    if summary:
        lines.append(summary + "\n")
    module = ".".join(path.relative_to(SOURCE.parent).with_suffix("").parts)
    imported_from = "plexosdb" if name in public_names() else module
    lines += ["## Import\n", f"```python\nfrom {imported_from} import {name}\n```\n"]

    if isinstance(node, ast.ClassDef):
        class_lines, class_members = render_class(node, path, route, revision)
        lines.extend(class_lines)
        members.extend(class_members)
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        lines += ["## Signature\n", f"```text\n{function_signature(node)}\n```\n"]
    else:
        lines += ["## Definition\n", f"```text\n{ast.unparse(node)}\n```\n"]
    return "\n".join(lines) + "\n", members


def module_source(module: str) -> Path:
    parts = module.removeprefix("plexosdb.").split(".")
    candidate = SOURCE.joinpath(*parts).with_suffix(".py")
    if candidate.is_file():
        return candidate
    package = SOURCE.joinpath(*parts, "__init__.py")
    if package.is_file():
        return package
    raise FileNotFoundError(f"No Python source found for {module}")


def module_entries() -> dict[str, list[tuple[str, Path]]]:
    return {
        page_slug: [(module, module_source(module)) for module in modules]
        for page_slug, modules in MODULES.items()
    }


def module_definitions(path: Path) -> list[ast.AST]:
    nodes = ast.parse(path.read_text()).body
    result = []
    for node in nodes:
        if isinstance(
            node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ) and not node.name.startswith("_"):
            result.append(node)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and not target.id.startswith("_") for target in targets):
                result.append(node)
    return result


def module_definition_name(node: ast.AST) -> str:
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return node.name
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    return next(
        target.id for target in targets if isinstance(target, ast.Name) and not target.id.startswith("_")
    )


def render_module_methods(
    module: str,
    name: str,
    methods: list[ast.FunctionDef | ast.AsyncFunctionDef],
    public_route: str,
    fragments: dict[str, str],
) -> list[str]:
    lines = ["##### Methods\n"]
    for method in methods:
        method_anchor = anchor(method.name)
        lines += [f"###### {method.name}\n", f"```text\n{function_signature(method)}\n```\n"]
        if summary := doc_summary(method):
            lines.append(summary + "\n")
        fragments[f"{module}.{name}.{method.name}"] = public_route + "#" + method_anchor
        fragments[f"plexosdb.{module.removeprefix('plexosdb.')}.{name}.{method.name}"] = (
            public_route + "#" + method_anchor
        )
    return lines


def render_module_class(
    module: str,
    name: str,
    node: ast.ClassDef,
    exported: set[str],
    public_route: str,
    fragments: dict[str, str],
) -> list[str]:
    lines = []
    methods = class_methods(node)
    if methods:
        lines.extend(render_module_methods(module, name, methods, public_route, fragments))
    if name in exported:
        object_route = f"/plexosdb/reference/python-api/{slug(name)}/"
        lines.append(f"Full reference: [`{name}`]({object_route}).\n")
        fragments[f"{module}.{name}"] = object_route
        fragments[f"plexosdb.{module.removeprefix('plexosdb.')}.{name}"] = object_route
    return lines


def render_module_definition(
    module: str,
    path: Path,
    node: ast.AST,
    revision: str,
    exported: set[str],
    public_route: str,
    fragments: dict[str, str],
) -> list[str]:
    name = module_definition_name(node)
    lines = [f"#### {name}\n", f"[Source]({source_url(path, node, revision)})\n"]
    if summary := doc_summary(node):
        lines.append(summary + "\n")
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        lines.append(f"```text\n{function_signature(node)}\n```\n")
    elif isinstance(node, ast.ClassDef):
        lines.extend(render_module_class(module, name, node, exported, public_route, fragments))
    else:
        lines.append(f"```text\n{ast.unparse(node)}\n```\n")
    name_anchor = anchor(name)
    fragments[f"{module}.{name}"] = public_route + "#" + name_anchor
    fragments[f"plexosdb.{module.removeprefix('plexosdb.')}.{name}"] = public_route + "#" + name_anchor
    return lines


def append_module_reference(
    page_slug: str,
    module_sources: list[tuple[str, Path]],
    revision: str,
    exported: set[str],
    fragments: dict[str, str],
) -> dict[str, str]:
    route = f"/reference/api/modules/{page_slug}/"
    public_route = f"/plexosdb{route}"
    destination = MODULE_PAGES / f"{page_slug}.md"
    lines = ["## Public module members\n"]
    for module, path in module_sources:
        lines.append(f"### {module}\n")
        for node in module_definitions(path):
            lines.extend(
                render_module_definition(module, path, node, revision, exported, public_route, fragments)
            )
    existing = destination.read_text()
    if GENERATED_START in existing:
        existing = existing.split(GENERATED_START, 1)[0].rstrip()
    else:
        existing = re.split(r"(?m)^## Public module members\s*$", existing, maxsplit=1)[0].rstrip()
    generated = "\n".join(lines).strip()
    destination.write_text(f"{existing}\n\n{GENERATED_START}\n\n{generated}\n\n{GENERATED_END}\n")
    return {"label": MODULE_LABELS[page_slug], "link": route}


def generate() -> None:
    names = public_names()
    root_definitions = root_export_definitions()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    PAGES.mkdir(parents=True, exist_ok=True)
    NAVIGATION.parent.mkdir(parents=True, exist_ok=True)
    expected = {slug(name) + ".md" for name in names}
    for stale in PAGES.glob("*.md"):
        if stale.name not in expected:
            stale.unlink()

    exports: list[dict[str, object]] = []
    fragments: dict[str, str] = {}
    exported = set(names)
    for name in sorted(set(names)):
        path, node = root_definitions[name]
        content, members = render_object(name, path, node, revision)
        (PAGES / f"{slug(name)}.md").write_text(content)
        module = ".".join(path.relative_to(SOURCE.parent).with_suffix("").parts)
        object_route = f"/plexosdb/reference/python-api/{slug(name)}/"
        fragments[f"plexosdb.{name}"] = object_route
        fragments[f"{module}.{name}"] = object_route
        for member in members[1:]:
            member_route = "/plexosdb" + member["link"]
            fragments[f"plexosdb.{module.removeprefix('plexosdb.')}.{name}.{member['label']}"] = member_route
            fragments[f"{module}.{name}.{member['label']}"] = member_route
        exports.append({"label": name, "collapsed": True, "items": members})

    modules = []
    for page_slug, module_sources in module_entries().items():
        modules.append(append_module_reference(page_slug, module_sources, revision, exported, fragments))
    FRAGMENTS.parent.mkdir(parents=True, exist_ok=True)
    FRAGMENTS.write_text(json.dumps(fragments, indent=2) + "\n")
    NAVIGATION.write_text(json.dumps({"exports": exports, "modules": modules}, indent=2) + "\n")
    print(f"Generated {len(exports)} public API pages and {len(modules)} module references")


if __name__ == "__main__":
    generate()
