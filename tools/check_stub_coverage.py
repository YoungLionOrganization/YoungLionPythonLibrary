#!/usr/bin/env python3
"""Dependency-free structural audit for YoungLion's public Python type stubs.

This is deliberately a structural check, not a full static type checker. It verifies that:
- every .pyi parses on the running Python,
- each direct public class/function in the maintained Python modules exists in its paired .pyi,
- each direct public method defined on those classes exists in the stub class,
- aliases, special methods, exports and API docstrings are present,
- properties and class/static methods preserve their calling conventions,
- native functions without keyword support have positional-only signatures,
- py.typed exists,
- the two application-facing search aliases are declared in search.pyi.

Run from the repository root:
    python tools/check_stub_coverage.py

Run tools/check_typing.py separately for semantic checking with mypy.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "YoungLion"

PAIRS = [
    (SRC / "DataModel" / "_core.py", SRC / "DataModel" / "_core.pyi"),
    (SRC / "DataModel" / "_variants.py", SRC / "DataModel" / "_variants.pyi"),
    (SRC / "DataModel" / "_collections.py", SRC / "DataModel" / "_collections.pyi"),
    (SRC / "DataModel" / "_models.py", SRC / "DataModel" / "_models.pyi"),
    (SRC / "DataModel" / "_cache.py", SRC / "DataModel" / "_cache.pyi"),
    (SRC / "DataModel" / "_parsing.py", SRC / "DataModel" / "_parsing.pyi"),
    (SRC / "function" / "_base.py", SRC / "function" / "_base.pyi"),
    (SRC / "function" / "_formats.py", SRC / "function" / "_formats.pyi"),
    (SRC / "function" / "_extra.py", SRC / "function" / "_extra.pyi"),
    (SRC / "function" / "_utilities.py", SRC / "function" / "_utilities.pyi"),
    (SRC / "search.py", SRC / "search.pyi"),
    (SRC / "Colors.py", SRC / "Colors.pyi"),
]

@dataclass(frozen=True)
class ModuleSurface:
    functions: set[str]
    classes: dict[str, set[str]]


def parse(path: Path) -> ast.Module:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        raise SystemExit(f"[stub-audit] syntax error in {path}: {exc}") from exc


def surface(tree: ast.Module) -> ModuleSurface:
    functions: set[str] = set()
    classes: dict[str, set[str]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            functions.add(node.name)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            methods = {
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                and (not child.name.startswith("_") or child.name.startswith("__"))
            }
            methods.update(
                target.id
                for child in node.body
                if isinstance(child, ast.Assign) and isinstance(child.value, ast.Name)
                and not child.value.id.startswith("_")
                for target in child.targets if isinstance(target, ast.Name)
                and (not target.id.startswith("_") or target.id.startswith("__"))
            )
            classes[node.name] = methods
    return ModuleSurface(functions, classes)


def declared_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def main() -> int:
    errors: list[str] = []
    pyi_files = sorted(SRC.rglob("*.pyi"))
    for pyi in pyi_files:
        parse(pyi)

    if not (SRC / "py.typed").is_file():
        errors.append("missing src/YoungLion/py.typed")

    checked_methods = 0
    checked_classes = 0
    checked_functions = 0
    for source_path, stub_path in PAIRS:
        src = surface(parse(source_path))
        stub = surface(parse(stub_path))
        checked_functions += len(src.functions)
        checked_classes += len(src.classes)
        for name in sorted(src.functions - stub.functions):
            errors.append(f"{source_path.relative_to(ROOT)}: public function {name!r} missing from {stub_path.name}")
        for class_name, methods in sorted(src.classes.items()):
            if class_name not in stub.classes:
                errors.append(f"{source_path.relative_to(ROOT)}: public class {class_name!r} missing from {stub_path.name}")
                continue
            checked_methods += len(methods)
            missing = methods - stub.classes[class_name]
            for method in sorted(missing):
                errors.append(f"{source_path.relative_to(ROOT)}: {class_name}.{method} missing from {stub_path.name}")

        source_tree, stub_tree = parse(source_path), parse(stub_path)
        def audit_scope(source: ast.AST, stub: ast.AST, prefix: str = "") -> None:
            stub_defs: dict[str, list[ast.AST]] = {}
            for node in stub.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    stub_defs.setdefault(node.name, []).append(node)
            for node in source.body:
                if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                matches = stub_defs.get(node.name, [])
                if not matches:
                    continue
                label = f"{source_path.relative_to(ROOT)}: {prefix}{node.name}"
                if not node.name.startswith("_") and not ast.get_docstring(matches[0]):
                    errors.append(f"{label}: stub lacks API documentation")
                if isinstance(node, ast.ClassDef):
                    audit_scope(node, matches[0], prefix + node.name + ".")
                    continue
                is_overloaded = any(
                    any(isinstance(d, ast.Name) and d.id == "overload" for d in m.decorator_list)
                    for m in matches
                )
                source_decorators = {ast.unparse(d) for d in node.decorator_list}
                for match in matches:
                    stub_decorators = {ast.unparse(d) for d in match.decorator_list}
                    for decorator in ("property", "classmethod", "staticmethod"):
                        if (decorator in source_decorators) != (decorator in stub_decorators):
                            errors.append(f"{label}: {decorator} differs between runtime and stub")
                if is_overloaded:
                    if any(not any(isinstance(d, ast.Name) and d.id == "overload" for d in m.decorator_list) for m in matches):
                        errors.append(f"{label}: overload implementation must not appear in a stub")
                    continue
                def shape(args: ast.arguments) -> tuple:
                    return (tuple(a.arg for a in args.posonlyargs), tuple(a.arg for a in args.args),
                            tuple(a.arg for a in args.kwonlyargs),
                            args.vararg.arg if args.vararg else None,
                            args.kwarg.arg if args.kwarg else None)
                if shape(node.args) != shape(matches[0].args):
                    errors.append(f"{label}: runtime/stub parameter names or calling convention differ")
        audit_scope(source_tree, stub_tree)

    # Public exports must exist even if a runtime fallback has been removed.
    for package in (SRC / "DataModel", SRC / "function"):
        tree = parse(package / "__init__.py")
        stub_names = declared_names(parse(package / "__init__.pyi"))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
                for name in ast.literal_eval(node.value):
                    if name not in stub_names:
                        errors.append(f"{package.name}/__init__.pyi: missing public export {name}")

    # Native methods without METH_KEYWORDS reject keyword arguments at runtime.
    native_stub = parse(SRC / "_native.pyi")
    native_defs = {n.name: n for n in native_stub.body if isinstance(n, ast.FunctionDef)}
    method_table = (SRC / "_native_part07.inc").read_text(encoding="utf-8")
    entries = re.findall(r'\{"(\w+)".*?,(METH_\w+(?:\|METH_\w+)*),"[^"]*"\}', method_table)
    for name, flags in entries:
        node = native_defs.get(name)
        if node is None:
            errors.append(f"_native.pyi: missing C++ callable {name}")
        elif "METH_KEYWORDS" not in flags and node.args.args:
            errors.append(f"_native.pyi: {name} must use positional-only parameters")

    search_stub = declared_names(parse(SRC / "search.pyi"))
    for alias in ("SearchEngine", "DDMIndex"):
        if alias not in search_stub:
            errors.append(f"search.pyi: missing public alias {alias}")

    if errors:
        print("[stub-audit] FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print(
        "[stub-audit] OK — "
        f"{len(pyi_files)} stub files parsed; "
        f"{checked_classes} public classes, {checked_methods} direct public methods, "
        f"{checked_functions} module-level public functions structurally covered."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
