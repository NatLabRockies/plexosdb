"""Extract and print simple Python function signatures from a source file."""

from __future__ import annotations

import ast
from pathlib import Path


def _parse_file(file_path: str | Path) -> ast.AST:
    """Parse a Python source file and return its AST."""
    return ast.parse(Path(file_path).read_text())


def _format_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Format all argument kinds from a function AST node."""
    args_list: list[str] = [arg.arg for arg in node.args.posonlyargs]
    if node.args.posonlyargs:
        args_list.append("/")

    args_list.extend(arg.arg for arg in node.args.args)

    if node.args.vararg:
        args_list.append(f"*{node.args.vararg.arg}")
    elif node.args.kwonlyargs:
        args_list.append("*")

    args_list.extend(arg.arg for arg in node.args.kwonlyargs)

    if node.args.kwarg:
        args_list.append(f"**{node.args.kwarg.arg}")

    return args_list


def extract_signatures(file_path: str | Path, methods: list[str]) -> dict[str, str]:
    """Extract signatures for selected methods from a Python source file."""
    tree = _parse_file(file_path)
    results: dict[str, str] = {}
    wanted = set(methods)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in wanted:
            args = _format_args(node)
            results[node.name] = f"def {node.name}({', '.join(args)})"

    return results


def _print_signatures_in_order(signatures: dict[str, str], methods: list[str]) -> None:
    """Print signatures in the same order as requested methods."""
    for method in methods:
        signature = signatures.get(method)
        if signature:
            print(signature)


methods = [
    "update_object",
    "update_property",
    "delete_property",
    "delete_object",
    "add_scenario",
    "list_parent_objects",
    "list_child_objects",
    "list_object_memberships",
    "iterate_properties",
    "validate_database",
    "backup_database",
    "to_csv",
    "list_models",
    "list_scenarios_by_model",
]

_print_signatures_in_order(extract_signatures("src/plexosdb/db.py", methods), methods)
