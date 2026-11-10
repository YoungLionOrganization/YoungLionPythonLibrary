"""Core Dynamic Data Model implementation.

This module defines :class:`DDM`, YoungLion's general-purpose hierarchical data
container.  DDM stores public fields directly in the instance ``__dict__`` to
avoid duplicate mapping storage while exposing mapping-like operations,
serialization, dotted-path traversal, schema validation, clone/merge/diff tools,
structure analysis and transformations.  Performance-sensitive recursive and
path operations delegate to the native ``YoungLion._native`` extension.

Subclassing is a first-class use case.  A domain model may call ``super().__init__``
with raw mapping data and then normalize selected attributes into richer types or
nested DDM subclasses.  Serialization continues to recurse through those nested
objects, and cloning re-runs conventional subclass constructors so domain types
are preserved whenever possible.

Example
-------
    class UserProfile(DDM):
        def __init__(self, data):
            super().__init__(data)
            self.country: str = str(data.get("country", "Unknown"))

    class User(DDM):
        def __init__(self, data):
            super().__init__(data)
            self.name: str = str(data.get("name", "Unknown"))
            self.profile: UserProfile = UserProfile(data.get("profile", {}))

    user = User({"name": "Alice", "profile": {"country": "AZ"}})
    assert user.get_path("profile.country") == "AZ"

DDM is dynamic rather than a validation framework: use SchemaDDM or explicit
subclass normalization when strict input contracts are required.
"""
TDefault = TypeVar('TDefault')
from typing import Optional
from collections.abc import ItemsView, Iterable, Iterator, KeysView, Mapping, ValuesView
from typing import Any, Callable, Dict, Type, TypeVar, Union, overload
from typing import TypedDict

class _SchemaValidation(TypedDict):
    """Native validation result, with readable errors and a success flag."""
    valid: bool
    errors: list[str]

class _DDMMemoryInfo(TypedDict):
    """Approximate byte counts; recursive_bytes counts shared nodes once."""
    object_bytes: int
    storage_bytes: int
    recursive_bytes: int
    nodes: int
    keys: int

class _DDMChange(TypedDict):
    """Changed field values; an absent side is represented by None."""
    old: Any
    new: Any

T_DDM = TypeVar('T_DDM', bound='DDM')

class DDM:
    """Dynamic Data Model.

    ``DDM`` provides hierarchical JSON-like application data with native path/serialization hot paths.

    When to use it
    --------------
    Subclass DDM when domain-specific typed attributes and methods should coexist with dynamic input.

    Data model semantics
    --------------------
    Public fields are stored once in the normal instance ``__dict__``. ``_data`` and ``_native_data`` are compatibility/native views of that same store rather than duplicate dictionaries. Nested DDM objects are recursively serialized, and ordinary mapping/list/tuple values remain valid inputs.

    Subclassing pattern
    -------------------
    Call ``super().__init__(data)`` first, then normalize the domain fields you care about into annotated attributes or nested DDM subclasses. This keeps raw JSON flexibility while making application code self-documenting and IDE-friendly.

    Example::

        class UserProfile(DDM):
            def __init__(self, data):
                super().__init__(data)
                self.name: str = str(data.get("name", "Unknown"))

        class User(DDM):
            def __init__(self, data):
                super().__init__(data)
                self.profile: UserProfile = UserProfile(data.get("profile", {}))

        user = User({"profile": {"name": "Alice"}})
        print(user.get_path("profile.name"))
        print(user.to_json())
    """
    _data: Dict[str, Any]
    _schema: Dict[str, Any] | None

    def __init__(self, data: Mapping[str, Any]) -> None:
        """Initialize a new DDM instance using the supplied configuration and input data.

        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.

        Raises
        ------
        TypeError
            If ``data`` is not a mapping.
        """
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Recursively convert public fields into ordinary dictionaries and lists.

        Private DDM fields beginning with an underscore are omitted. Mapping keys beginning with an underscore are retained inside ordinary dictionaries. DDM subclass boundaries are removed; this is a data snapshot, unlike to_string(), which preserves model names. Tuples/sets become lists in the native conversion. Cyclic or excessively deep containers raise RecursionError.
        """
        ...

    def to_json(self, indent: int=2, include_private: bool=False) -> str:
        """Serialize public data to JSON text using the native encoder.

        indent=2 pretty-prints; indent=-1 selects compact output. include_private=True adds the diagnostic _data and _schema envelope. Use to_string() for bounded human-readable display and to_json() for machine-readable data. Cyclic or excessively deep containers raise RecursionError.
        """
        ...

    @staticmethod
    def from_json(json_str: str) -> DDM:
        """Create a DDM instance from a JSON object string.

        Parameters
        ----------
        json_str : str
            Value supplied for ``json_str`` according to the DDM contract.

        Returns
        -------
        New DDM containing the decoded JSON object.

        Raises
        ------
        ValueError
            If the JSON root is not an object or input cannot be decoded according to the JSON contract.
        """
        ...

    @overload
    def get_path(self, path: str) -> Any | None:
        """Read a nested value using a dotted path without manually traversing every intermediate object.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.

        Returns
        -------
        Resolved nested value or ``default`` when the path cannot be resolved.

        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.

        Example::

            user.get_path("profile.address.city", "Unknown")
        """
        ...

    @overload
    def get_path(self, path: str, default: TDefault) -> Any | TDefault:
        """Read a nested value using a dotted path without manually traversing every intermediate object.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.

        Returns
        -------
        Resolved nested value or ``default`` when the path cannot be resolved.

        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.

        Example::

            user.get_path("profile.address.city", "Unknown")
        """
        ...

    def set_path(self, path: str, value: Any) -> bool:
        """Assign a nested value using a dotted path, creating or updating the addressed field according to DDM path semantics.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.

        Returns
        -------
        ``True`` when the native path assignment succeeds.

        Notes
        -----
        This is a mutation. If the DDM belongs to an externally managed search index, refresh or invalidate that index unless the owning YoungLion collection performed the mutation and handled invalidation.
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.

        Example::

            user.set_path("profile.locale", "en-US")
        """
        ...

    def has_path(self, path: str) -> bool:
        """Return whether a dotted path can be resolved in the current object.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.

        Returns
        -------
        Boolean indicating whether the full dotted path exists.

        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        ...

    def clone(self: T_DDM) -> T_DDM:
        """Deep-copy public container data and reconstruct the same DDM subclass.

        Built-in variants supply their own reconstruction hook. Conventional subclasses are recreated with cls(data); if that constructor rejects the shape with TypeError, base initialization is used on a new instance. Schema state is copied. Arbitrary opaque leaf objects may retain identity; this is not a general-purpose pickle/deepcopy implementation. Cyclic input raises RecursionError.
        """
        ...

    def copy(self: T_DDM) -> T_DDM:
        ...

    def to_flat_dict(self, prefix: str='', separator: str='.') -> Dict[str, Any]:
        """Flatten nested structured data into a single mapping whose keys encode paths.

        Parameters
        ----------
        prefix : str (default: ``''``)
            Optional path/text prefix applied by the operation.
        separator : str (default: ``'.'``)
            Delimiter inserted between flattened path components.


        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.

        Example::

            DDM({"profile": {"name": "Alice"}}).to_flat_dict()
            # {"profile.name": "Alice"}
        """
        ...

    def merge(self: T_DDM, other: DDM | Mapping[str, Any]) -> T_DDM:
        """Deep-merge another DDM or mapping into this object and return the mutated instance.

        Parameters
        ----------
        other : Union['DDM', Mapping[str, Any]]
            Another compatible object/value used by the operation.
        """
        ...

    def update(self: T_DDM, *args: Mapping[str, Any], **kwargs: Any) -> T_DDM:
        """Update top-level fields from mapping arguments and keyword values.

        Parameters
        ----------
        *args : Mapping[str, Any]
            Arguments passed to a script/callable/subprocess.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        ...

    def diff(self, other: DDM) -> Dict[str, _DDMChange]:
        """Compute structural/value differences between this DDM and another DDM.

        Parameters
        ----------
        other : 'DDM'
            Another compatible object/value used by the operation.
        """
        ...

    def validate_schema(self, schema: Dict[str, Any]) -> _SchemaValidation:
        """Validate the current data against a schema and remember that schema on the object.

        Parameters
        ----------
        schema : Dict[str, Any]
            Schema mapping describing expected fields/types/constraints.


        Notes
        -----
        The returned mapping reports validation status/errors according to the native schema contract. Validation records the schema on the object for diagnostic/variant use; ordinary DDM remains mutable.
        """
        ...

    def keys(self) -> KeysView[str]:
        """Return a dynamic view of top-level field names.

        Returns
        -------
        Result collection/value produced by the operation.
        """
        ...

    def values(self) -> ValuesView[Any]:
        """Return a dynamic view or collection of stored values.

        Returns
        -------
        Result collection/value produced by the operation.
        """
        ...

    def items(self) -> ItemsView[str, Any]:
        """Return key/value pairs for the current mapping-like object.

        Returns
        -------
        Result collection/value produced by the operation.
        """
        ...

    @overload
    def get(self, key: str) -> Any | None:
        """Return a value for a key, falling back to a default when the key is absent.

        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        """
        ...

    @overload
    def get(self, key: str, default: TDefault) -> Any | TDefault:
        """Return a value for a key, falling back to a default when the key is absent.

        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        """
        ...

    def setdefault(self, key: str, default: Any=None) -> Any:
        """Return the existing value for a key or insert and return the supplied default.

        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        """
        ...

    @overload
    def pop(self, key: str) -> Any:
        """Remove a key and return its value, optionally using a default when absent.

        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        default : Any (default: ``_MISSING``)
            Fallback returned/used when the requested value or path is absent.
        """
        ...

    @overload
    def pop(self, key: str, default: TDefault) -> Any | TDefault:
        """Remove a key and return its value, optionally using a default when absent.

        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        default : Any (default: ``_MISSING``)
            Fallback returned/used when the requested value or path is absent.
        """
        ...

    def popitem(self) -> tuple[str, Any]:
        """Remove and return one key/value pair using normal dictionary popitem semantics."""
        ...

    def clear(self) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class."""
        ...

    def filter_keys(self, keys: Iterable[str]) -> DDM:
        """Return a base DDM with the requested existing fields in source order.

        Missing field names are ignored. Values are shared with the source (a shallow field selection). only() is the positional-argument equivalent. The source model is not mutated.
        """
        ...

    def exclude_keys(self, keys: Iterable[str]) -> DDM:
        """Create a new DDM excluding the requested top-level keys.

        Parameters
        ----------
        keys : Iterable[str]
            Iterable of mapping field names.
        """
        ...

    def pick(self, *keys: str) -> DDM:
        """Convenience wrapper that returns a DDM containing only the named keys.

        Parameters
        ----------
        *keys : str
            Iterable of mapping field names.
        """
        ...

    def omit(self, *keys: str) -> DDM:
        """Convenience wrapper that returns a DDM without the named keys.

        Parameters
        ----------
        *keys : str
            Iterable of mapping field names.
        """
        ...

    def search(self, query: Any, case_sensitive: bool=False) -> Dict[str, Any]:
        """Search the current data/index using the query and options supported by this class.

        Parameters
        ----------
        query : Any
            Search text, structured query or SQL/XML expression according to the method.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    def find_by_type(self, value_type: Type[Any]) -> Dict[str, Any]:
        """Return flattened values whose runtime type matches the requested type.

        Parameters
        ----------
        value_type : Type[Any]
            Runtime Python type used for filtering/type checks.
        """
        ...

    def transform(self, func: Callable[[Any], Any]) -> DDM:
        """Apply a callable to values and return a transformed DDM rather than mutating the original.

        Parameters
        ----------
        func : Callable[[Any], Any]
            Callable applied by the operation.
        """
        ...

    def map_attributes(self, mapping: Mapping[str, str | Callable[[Any], Any]]) -> DDM:
        """Return a base DDM with selected fields renamed or transformed.

        Each mapping entry is an existing field name and either a new field name or a callback receiving its value. Absent fields are ignored. Operations follow mapping order; renaming onto an existing name overwrites it. Nested data is first converted with to_dict().
        """
        ...

    def sort_by_key(self, reverse: bool=False) -> DDM:
        """Return a DDM whose top-level items are ordered by key.

        Parameters
        ----------
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        """
        ...

    def sort_by_value(self, reverse: bool=False) -> DDM:
        """Return a DDM whose top-level items are ordered by value.

        Parameters
        ----------
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        """
        ...

    def group_by(self, func: Callable[[str, Any], Any]) -> Dict[Any, Dict[str, Any]]:
        """Group top-level fields with func(key, value).

        Returns {group_key: {field_name: original_value}}. Values are shared with the source. The callback must produce hashable group keys. The model is not mutated.
        """
        ...

    def aggregate(self, funcs: Callable[[Iterable[Any]], Any] | Mapping[str, Callable[[Iterable[Any]], Any]]) -> Any:
        """Aggregate top-level values with a callable or a mapping of named callables.

        A single callable receives the values view and its result is returned directly. A mapping of callables receives one shared tuple snapshot of the values and produces a dictionary with the same names. No model mutation is performed.
        """
        ...

    def get_types(self) -> Dict[str, Type[Any]]:
        """Return a mapping of each stored field name to its Python type object.

        Values are types such as int and str, not type-name strings. Only top-level fields are inspected; nested structure is unchanged.
        """
        ...

    def has_type(self, key: str, value_type: Type[Any]) -> bool:
        """Check whether a named field currently contains a value of the requested type.

        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        value_type : Type[Any]
            Runtime Python type used for filtering/type checks.
        """
        ...

    def count(self) -> int:
        """Return the number of stored values or matching records, depending on the class.

        Returns
        -------
        Number of records/fields matching the method semantics.
        """
        ...

    def is_empty(self) -> bool:
        """Return True when the object has no public data fields."""
        ...

    def memory_info(self, recursive: bool=True) -> _DDMMemoryInfo:
        """Return approximate storage metrics useful for comparing data representations.

        Parameters
        ----------
        recursive : bool (default: ``True``)
            Value supplied for ``recursive`` according to the DDM contract.
        """
        ...

    def compact(self: T_DDM, intern_keys: bool=True) -> T_DDM:
        """Apply optional key interning/compaction steps intended to reduce repeated-memory overhead.

        Parameters
        ----------
        intern_keys : bool (default: ``True``)
            Whether repeated string keys should be interned to reduce memory overhead.
        """
        ...

    def to_csv(self) -> str:
        """Serialize the represented data to CSV text."""
        ...

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __contains__(self, key: object) -> bool:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...

    def __eq__(self, other: object) -> bool:
        ...

    def __repr__(self) -> str:
        """Return an uncolored hierarchy bounded to depth 3 and 10 children per container. Recursive references are marked; no to_dict() conversion is performed.

        """

    def if_exists(self: T_DDM, key: str) -> T_DDM | None:
        """Return this model if a stored field exists, otherwise None.

        Unlike hasattr(), this checks data fields rather than methods. A field
        containing None still exists. No field is created by this operation.
        """
        ...

    def ensure(self: T_DDM, key: str, default: Any=None) -> T_DDM:
        """Insert a missing field and return self; preserve existing None values.

        Uses the model's item assignment so immutable variants reject writes.
        The default is stored by reference, matching setdefault().
        """
        ...

    def only(self, *keys: str) -> 'DDM':
        """Return a new DDM containing the requested existing fields."""
        ...

    def without(self, *keys: str) -> 'DDM':
        """Return a new DDM excluding the supplied fields; ignore absent names."""
        ...

    def to_csv_line(self, sep: str=',') -> str:
        """Export one CSV record in field order, without a trailing record newline.

        ``sep`` is a one-character delimiter. Python's CSV quoting preserves
        delimiters, quotes and embedded newlines. None becomes an empty field;
        other values use str(), as in csv.writer. Headers are not included.
        """
        ...

    @staticmethod
    def from_csv_line(csv_line: str, headers: Iterable[str], sep: str=',') -> 'DDM':
        """Parse exactly one quoted CSV record; field values remain strings.

        Raise ValueError for multiple records, duplicate headers or a header/
        value count mismatch. Invalid CSV quoting raises csv.Error. Unlike the
        historical split-based parser, embedded delimiters/newlines round-trip.
        """
        ...

    def to_xml_like(self, tag: str='item', indent: int=0) -> str:
        """Export fields as escaped text elements beneath an XML root.

        This compatibility helper is flat: nested values become display text.
        Element names must be simple XML names; invalid names raise ValueError.
        ``indent`` is the starting level, with two spaces per level.
        """
        ...

    def to_string(self, indent: int=2, *, color: Optional[bool]=None, max_depth: int=8, max_items: int=50, sort_keys: bool=False, include_private: bool=False) -> str:
        """Return a readable hierarchy of model, mapping and container values.

        DDM subclass names, string quoting and container boundaries remain
        visible. Recursive references become ``<recursion: Type>``. Each
        container shows at most ``max_items`` children; containers at
        ``max_depth`` are abbreviated. Long scalar representations are bounded.
        Shared children are rendered normally unless they form an active cycle.
        No serialization, cloning or lazy-field evaluation is performed.

        ``indent`` is the non-negative number of spaces per level. ``max_depth``
        is between 0 and 100; ``max_items`` is non-negative. Invalid limits raise
        TypeError/ValueError. ``sort_keys`` sorts mappings by key type and repr;
        otherwise insertion order is preserved. Private DDM fields are hidden
        unless ``include_private=True``; internal slots are never displayed.

        ``color=None`` enables ANSI colors only for a terminal stdout when
        NO_COLOR is absent and TERM is not dumb. Pass False for stable log/test
        output or True to explicitly request color. Use to_json() for JSON.

        Example::

            model = DDM({"user": DDM({"name": "Leyla"}), "roles": ["admin"]})
            print(model.to_string(color=False, max_depth=4))
        """
        ...

    def __str__(self) -> str:
        """Return the bounded hierarchical display; use to_json() for JSON text."""
        ...

    def __getattr__(self, name: str) -> Any:
        """Dynamically stored data attributes have runtime-dependent types.

        Declare attributes on a DDM subclass for precise static types. This stub models attribute lookup from instance data; absent attributes raise AttributeError at runtime.
        """

    @property
    def _native_data(self) -> Dict[str, Any]:
        """Internal zero-copy storage hook used by the C++ extension."""
        ...
    copy = clone
