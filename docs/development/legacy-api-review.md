# v0.0.9.9 → v0.1.1 API review

The comparison uses the actual v0.0.9.9 source at `b3e902e` and the latest
published repository tag, v0.1.1 at `8149638`. Their version metadata, README,
release descriptions, implementation and exported APIs were inspected together.
The modern modular API and dependency-free native architecture remain the base.

## Gaps completed

| Area | Changes |
|---|---|
| DDM display | Reintroduced a readable hierarchy, now covering nested mappings, model names, lists/tuples/sets, cycles, private-field selection, color detection, sorting and truncation. Added an explicit configurable `to_string()` API |
| DDM helpers | Restored `if_exists`, `ensure`, `only`, `without`, `to_csv_line`, `from_csv_line`, `to_xml_like` |
| Parsing and batch helpers | Restored `ParseError`, `split_any`, `ensure_int_list`, `enable_ansi`, `flatten_to_single_dict` and package exports |
| Size | Tuple conversion, separate width/height scaling, `fit_within`, clamping, transpose and scalar multiplication |
| Point | Tuple conversion, normalization, distance predicate, rotation, clamping, reflections and arithmetic operators |
| Range and Dataset | Fixed descending range iteration and nonadvancing steps; restored the documented Dataset population `variance` statistic and configurable CSV delimiter |
| Color | RGB/RGBA/Pillow tuples, normalized tuples, packed integer/CSS/lowercase hex conversion, opacity predicates, brightness, lighten/darken/invert/grayscale/alpha/saturation transformations and HSL/HSV conversion |
| SmartCache | Independent template retrieval/cloning, `report` alias, and `recursive=False` completion for individual records and batches |
| TextProcessor | Restored `find_keywords`, `replace_text`, `remove_stopwords`, `unique_words`, `text_summary`, `find_longest_word`, `calculate_readability` using the current text implementation |
| FileTransferManager | Restored `check_transfer_status` as the historical status entry point |
| ListDDM | Implemented the slice assignment advertised by the stubs, with record conversion, extended-slice checks and search-index invalidation |
| Type information | Expanded all `.pyi` files, corrected properties and enum members, covered operators, context managers, dataclass constructors, aliases/exports, callbacks and native calling conventions |

Native conversion, JSON encoding and deep container copies now participate in
CPython's recursion accounting. Cyclic serialization raises `RecursionError`;
string/repr display marks cycles directly. Opaque non-container leaf objects can
still retain identity when cloned, as in the existing native data-copy contract.

The old release text called `DDM.merge()` non-destructive, but both the old and
current implementations mutate and return the receiving model. The maintained
contract documents that behavior; use `model.clone().merge(other)` to keep the
source unchanged. Likewise, SmartCache's full template-copy/merge path should not
be described as processing only missing keys. No unmeasured performance claims
are inferred from historical release prose.

## Deliberate migration boundaries

This work does not replace the v0.1 architecture with the old implementation.
Applications should continue to use current documented constructors and return
types. In particular:

- `DDM.pick()` returns a DDM; `validate_schema()` returns a dictionary containing
  `valid` and `errors`; `get_types()` returns type objects. The old dictionary/
  tuple/type-name return shapes are not silently reintroduced.
- Size's `area`, `perimeter` and `aspect_ratio` are properties. Modern numeric
  constructors preserve floating-point units. Old automatic string/sequence
  constructor keyword forms are not added to every modern model; parsing helpers
  are explicitly available for conversion.
- `str(Size)`, `str(Point)` and `str(Color)` provide concise representations;
  `to_string()` on models uses the common configurable DDM formatter.
- File operations already provided by inherited File mixins are not missing
  functions. The modern PDF/YAML/SFTP scope and third-party dependency boundaries
  remain as documented in the format and compatibility references.
- CSV record helpers now use standard CSV quoting and reject mismatched field
  counts/duplicate headers instead of silently truncating values.
- `SmartCache` retains current statistics, validation and return shapes.
  `get_template()` and `clone_with_template()` return independent template data.
- `str(DDM)` is a human-readable hierarchy. Code that parsed v0.1.1's `str(DDM)`
  as JSON must call `to_json()` explicitly.

Dataset's row-oriented `group_by` / `aggregate` and ListDDM's fluent `reverse`
intentionally differ from similarly named inherited operations. The stubs keep
their accurate concrete signatures and narrowly annotate these existing
inheritance conflicts; they do not disable checking for the rest of the package.

## Verification

Run the behavioral suite, structural audit and semantic typing examples:

```bash
python -m pytest
python tools/check_stub_coverage.py
python tools/check_typing.py
```

The typing check targets the Python 3.10 language/type surface and checks every
stub plus application examples covering subclass clones/chaining, default values,
slicing, in-place literal returns, mapping views, operators, properties,
dataclass initialization, context management and callback result inference.

Build wheel/sdist artifacts and verify `.pyi`, `py.typed` and the new helper
modules are included. The wheel should contain the compiled extension and no
`.cpp`/`.inc` source; the sdist must contain native source fragments and tests.
