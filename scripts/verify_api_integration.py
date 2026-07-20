#!/usr/bin/env python3
"""Verify API-client → MCP-tool integration coverage for clarity-api.

clarity-api is a REST client for the Microsoft Clarity Data Export API. Its
public API surface (e.g. ``get_data_export``) lives in the modular
``clarity_api/api/`` package and is composed into the ``Api`` facade. The MCP
tools that surface those methods live in ``clarity_api/mcp/`` (e.g. the
``clarity_insights`` tool dispatches to ``client.get_data_export``).

This check walks the whole package: it collects every public API-client method
defined on an ``*Api*``/``*Client*`` class and confirms each is invoked by an
MCP tool. Inherited/composed layouts are handled by scanning all modules, not
just the thin facade files, so the parity check validates the real REST surface
rather than passing as a no-op.
"""

import ast
import glob
import os
import sys

# Per-agent minimum required integration coverage (percent). clarity-api
# surfaces its full REST export surface through the ``clarity_insights`` tool.
BASELINES = {
    "clarity-api": 100.0,
}

# Methods that are infrastructure rather than part of the REST surface and so
# are not expected to be surfaced as standalone MCP tools.
NON_SURFACE_METHODS = {
    "authenticate",
    "api_request",  # generic passthrough escape hatch, not a domain tool
}


def _iter_python_files(agent_dir):
    for path in glob.glob(os.path.join(agent_dir, "**", "*.py"), recursive=True):
        parts = path.split(os.sep)
        if any(
            seg in parts
            for seg in (
                ".venv",
                "venv",
                "node_modules",
                "__pycache__",
                "tests",
                "test",
            )
        ):
            continue
        yield path


def collect_api_methods(agent_dir):
    """Public methods defined on API/Client classes across the package."""
    methods: dict[str, dict[str, object]] = {}
    for filepath in _iter_python_files(agent_dir):
        try:
            with open(filepath, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            class_name = node.name.lower()
            is_api_class = (
                "api" in class_name or "client" in class_name or node.name == "Api"
            )
            if not is_api_class:
                continue
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith("_"):
                        continue
                    if item.name in NON_SURFACE_METHODS:
                        continue
                    methods.setdefault(
                        item.name, {"line": item.lineno, "class": node.name}
                    )
    return methods


class MethodCallVisitor(ast.NodeVisitor):
    """Collect attribute/getattr calls made on client-like objects."""

    def __init__(self):
        self.called_methods = set()

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id in (
            "client",
            "api",
            "self",
            "service",
        ):
            self.called_methods.add(node.attr)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if (
                len(node.args) >= 2
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id in ("client", "api")
                and isinstance(node.args[1], ast.Constant)
            ):
                self.called_methods.add(node.args[1].value)
        self.generic_visit(node)


def collect_tool_method_calls(agent_dir, api_methods):
    """API-client methods invoked by MCP tool modules across the package.

    A "tool module" is any module under an ``mcp`` package, an ``mcp_server.py``
    entrypoint, or any module defining a function decorated with ``@mcp.tool``.
    The whole module body is scanned so methods called inside nested tool
    closures (``register_*_tools``) are detected.
    """
    mapped = set()
    for filepath in _iter_python_files(agent_dir):
        rel = os.path.relpath(filepath, agent_dir)
        parts = rel.split(os.sep)
        is_mcp_module = "mcp" in parts or os.path.basename(filepath) == "mcp_server.py"
        try:
            with open(filepath, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            continue

        if not is_mcp_module:
            # Still inspect modules that define an @mcp.tool decorated function.
            has_tool = False
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for dec in node.decorator_list:
                        target = dec.func if isinstance(dec, ast.Call) else dec
                        if isinstance(target, ast.Attribute) and target.attr == "tool":
                            has_tool = True
            if not has_tool:
                continue

        visitor = MethodCallVisitor()
        visitor.visit(tree)
        mapped.update(visitor.called_methods.intersection(api_methods.keys()))
    return mapped


def verify_agent(agent_dir):
    api_methods = collect_api_methods(agent_dir)
    if not api_methods:
        return None
    mapped_methods = collect_tool_method_calls(agent_dir, api_methods)

    total = len(api_methods)
    covered = len(mapped_methods)
    coverage = (covered / total) * 100 if total else 0.0
    unmapped = set(api_methods.keys()) - mapped_methods

    return {
        "agent_name": os.path.basename(agent_dir.rstrip(os.sep)),
        "total_methods": total,
        "covered_methods": covered,
        "coverage": coverage,
        "unmapped": sorted(unmapped),
        "mapped": sorted(mapped_methods),
    }


def main():
    args = sys.argv[1:]

    if "--local" in args or "--pre-commit" in args:
        cwd = os.getcwd()
        res = verify_agent(cwd)
        if not res:
            print(
                "Skipping integration parity verification: no API-client "
                "methods found in current directory."
            )
            sys.exit(0)

        agent_name = res["agent_name"]
        coverage = res["coverage"]
        baseline = BASELINES.get(agent_name, 0.0)

        print(f"=== API-to-MCP Integration Parity Check for: {agent_name} ===")
        print(f"- API client methods: {res['total_methods']}")
        print(f"- Integrated methods: {res['covered_methods']}")
        print(f"- Mapped methods    : {', '.join(res['mapped']) or '(none)'}")
        print(f"- Current Coverage  : {coverage:.1f}%")
        print(f"- Target Baseline   : {baseline:.1f}%")

        if coverage < (baseline - 0.05):
            print(
                f"\nFAILED: Integration coverage ({coverage:.1f}%) is below the "
                f"required baseline of {baseline:.1f}%."
            )
            if res["unmapped"]:
                print("\nUnmapped API methods:")
                for m in res["unmapped"]:
                    print(f"  - {m}")
            sys.exit(1)

        print("\nPASSED: Integration coverage meets or exceeds the baseline.")
        sys.exit(0)

    # Workspace-wide scan
    agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    agent_dirs = [
        d for d in glob.glob(os.path.join(agents_dir, "*")) if os.path.isdir(d)
    ]
    results = []
    for agent_dir in sorted(agent_dirs):
        if os.path.basename(agent_dir).startswith(".") or "venv" in agent_dir:
            continue
        try:
            res = verify_agent(agent_dir)
            if res:
                results.append(res)
        except Exception as e:
            print(f"Operation failed: {type(e).__name__}", file=sys.stderr)

    print("# API to MCP Integration Parity Report")
    print(f"Scan Directory: `{agents_dir}`\n")
    print("| Agent Name | API Methods | Covered Methods | Coverage % | Status |")
    print("|---|---|---|---|---|")
    for r in results:
        status = "100%" if r["coverage"] >= 100.0 else "Parity Gap"
        print(
            f"| {r['agent_name']} | {r['total_methods']} | "
            f"{r['covered_methods']} | {r['coverage']:.1f}% | {status} |"
        )


if __name__ == "__main__":
    main()
