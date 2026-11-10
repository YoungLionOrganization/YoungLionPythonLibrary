# DDM core API

`DDM` is a mutable dynamic record. Top-level keys become attributes while mapping-like operations remain available.

```python
user = DDM({"name": "Alice", "profile": {"age": 30}})
print(user.name, user["name"])
user.set_path("profile.age", 31)
```

Key areas: serialization (`to_dict`, `to_json`, `to_flat_dict`), nested paths, clone/copy, merge/update, diff/schema validation, pick/omit/filter, transforms, grouping/aggregation, type/memory introspection and dict-style mutation.

Standard mutable DDM is not the recommended Python set/dict-key type. Use `FrozenDDM` for immutable value hashing or `IdentityDDM` for mutable identity semantics.

## Human-readable display

```python
from YoungLion import DDM

model = DDM({"profile": DDM({"name": "Çağrı"}), "roles": ["admin"]})
print(model.to_string(color=False, max_depth=4, max_items=20))
```

```text
DDM({
  'profile': DDM({
    'name': 'Çağrı',
  }),
  'roles': [
    'admin',
  ],
})
```

`str(model)` uses `to_string()` with its defaults. Unlike the JSON display in
v0.1.1, this output preserves subclass names and distinguishes tuples, sets and
lists. Use `model.to_json()` whenever another program expects JSON. `repr(model)`
uses the same formatter without ANSI colors, with depth 3 and 10 children per
container. Size, Point and Color retain concise geometry/color `str()` output;
their inherited `to_string()` provides the configurable hierarchy.

| Option | Default | Behavior |
|---|---|---|
| `indent` | `2` | Non-negative spaces per nesting level |
| `color` | `None` | Detect terminal stdout; honor `NO_COLOR` and `TERM=dumb`. True/False explicitly force/disable color |
| `max_depth` | `8` | Container expansion depth, from 0 to 100; deeper containers show `...` |
| `max_items` | `50` | Children shown per container; additional children have a truncation marker |
| `sort_keys` | `False` | Sort mapping keys by type name and repr instead of insertion order |
| `include_private` | `False` | Include underscore-prefixed DDM fields; internal slots remain hidden |

The formatter walks the original containers without calling `to_dict()` or
evaluating missing lazy fields. It limits long scalar representations and marks
cycles as `<recursion: DDM>` / `<recursion: list>` / `<recursion: dict>`. Reusing a
child in two separate branches is allowed and displays both copies normally.
Sorting requires visiting all keys of the mapping being sorted; without sorting,
at most `max_items + 1` visible entries are consumed per displayed container.
Custom opaque objects can execute their own `repr()` method during display.

`to_dict()`, `to_json()` and `clone()` require acyclic, reasonably nested data.
Native recursion guards raise `RecursionError` for cyclic/excessively deep input;
the display formatter is the appropriate tool for inspecting such data.

## Restored compatibility helpers

`if_exists(key)` returns the same model or None, checking stored fields rather
than class methods. `ensure(key, default)` inserts only when the field is absent
and returns self; an existing None is preserved. Immutable variants reject a new
field. `only(*keys)` / `without(*keys)` return shallow field selections as base
DDM objects, matching `filter_keys()` / `exclude_keys()`.

`to_csv_line(sep=",")` writes one properly quoted record without its trailing
record newline. `DDM.from_csv_line(line, headers, sep=",")` reads exactly one
record, retaining strings and validating field count and unique headers. Quoted
delimiters, quotes and embedded newlines round-trip. This replaces the historical
backslash escaping and split-based parser, which could silently lose data.

`to_xml_like(tag="item", indent=0)` writes a flat XML text element per field,
escaping `&`, `<` and `>`. Element names must match the documented simple ASCII
XML-name subset; invalid names raise ValueError. This helper does not recursively
map nested objects into an XML schema.
