# Maintaining the type stubs

Public API changes are incomplete until the corresponding `.pyi` surface is updated.

## Required workflow

1. Change the runtime implementation.
2. Update the matching modular `.pyi` file.
3. Update re-exports/aliases in package `__init__.pyi` files if needed.
4. Update `_native.pyi` when a native symbol changes.
5. Run `python tools/check_stub_coverage.py`.
   Run `python tools/check_typing.py` for semantic checking of all stubs and the
   examples in `tests/typing/public_api.py` (requires mypy from the dev extra).
6. Run the runtime test suite.
7. Build a wheel and verify `.pyi` files plus `py.typed` are present.

## Module mapping

| Runtime | Stub |
|---|---|
| `DataModel/_core.py` | `DataModel/_core.pyi` |
| `DataModel/_variants.py` | `DataModel/_variants.pyi` |
| `DataModel/_collections.py` | `DataModel/_collections.pyi` |
| `DataModel/_models.py` | `DataModel/_models.pyi` |
| `DataModel/_cache.py` | `DataModel/_cache.pyi` |
| `DataModel/_parsing.py` | `DataModel/_parsing.pyi` |
| `function/_base.py` | `function/_base.pyi` |
| `function/_formats.py` | `function/_formats.pyi` |
| `function/_extra.py` | `function/_extra.pyi` |
| `function/_utilities.py` | `function/_utilities.pyi` |
| `search.py` | `search.pyi` |
| `Colors.py` | `Colors.pyi` |
| native C++ module | `_native.pyi` |

## Dynamic APIs

Do not over-promise types for arbitrary dotted paths. `get_path("profile.name")` depends on a runtime string; `Any` is more accurate than inventing a generic that cannot be inferred. Provide precise typing for container shapes, fixed method returns, result objects and callbacks where the type checker can genuinely use it.

## Aliases

Aliases such as `SearchEngine = ApplicationSearch`, `DDMIndex = DDMPathIndex`, and `SC = SmartCache` must appear in stubs as well as runtime exports.

The structural audit also checks explicit package exports, operators/context
managers, decorator parity, parameter names and calling conventions. Native
functions registered without `METH_KEYWORDS` must use `/` in their signatures.
Overload implementations must be omitted from `.pyi` files, and `inplace`
overloads must use `Literal` plus a fallback for non-literal booleans.
