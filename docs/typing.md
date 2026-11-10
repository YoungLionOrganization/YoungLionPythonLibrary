# Typing and `.pyi` support

YoungLion is a PEP 561 typed package (`py.typed`). Public APIs and `_native` are described by modular stubs.

```text
YoungLion/
├── __init__.pyi
├── _native.pyi
├── search.pyi
├── Colors.pyi
├── DataModel/{__init__,_core,_variants,_collections,_models,_cache,_parsing}.pyi
└── function/{__init__,_base,_formats,_extra,_utilities}.pyi
```

The stubs model generics such as `DictDDM[str]`, DDM defaults/overloads, collection slices, aliases (`pluck`, `where`, `sub`, `mul`), dataclass fields, inherited `File` mixins and native functions.

An AST coverage check compares source/stub public classes, functions and methods so missing public signatures are caught during release preparation.

Stubs also carry the API documentation used for editor hovers. The structural
audit checks special methods, aliases, package exports, property/class/static
decorators, calling conventions and positional-only native functions.

```bash
python tools/check_stub_coverage.py
python tools/check_typing.py
```

The second command requires the `dev` extra (or mypy >= 1.15). It checks all stubs
and application-facing inference examples against the Python 3.10 type surface.
Collection `inplace` flags use `Literal` overloads, so `sort_by(..., inplace=True)`
preserves the collection type while the default returns a list. Retry/circuit
breaker callbacks preserve both argument checking and their result type through
`ParamSpec`. Dynamic dotted paths still return `Any`, because their values cannot
be inferred from an arbitrary runtime string.
