"""Specialized Dynamic Data Model variants.

The classes in this module intentionally change one important semantic property
of ordinary :class:`DDM`: mutability, equality/hash behavior, storage layout,
schema enforcement, missing-value behavior, lazy computation or ownership of the
underlying mapping.  They are designed to be selected deliberately rather than
used as interchangeable aliases.

Use FrozenDDM for immutable value objects, IdentityDDM for mutable objects that
must participate in identity-based sets/maps, PackedDDM for dense read-heavy
record pools, SchemaDDM for runtime validation, DefaultDDM for generated missing
values, LazyDDM for cached derived fields and ViewDDM for zero-copy access to an
existing mutable mapping.
"""
from collections.abc import Iterator, Mapping
from typing import Any, Callable, Dict, TypeVar, overload
from ._core import DDM, _SchemaValidation, _DDMMemoryInfo
T = TypeVar('T')

class FrozenDDM(DDM):
    """Immutable DDM value object.

    ``FrozenDDM`` provides recursive immutability plus value equality/hash semantics.

    When to use it
    --------------
    Use for configuration snapshots, cache keys and set/dict membership when content must not change.
    """

    def __init__(self, data: Mapping[str, Any]) -> None:
        """Initialize a new FrozenDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        """
        ...

    def __setattr__(self, name: str, value: Any) -> None:
        """Reject public field writes once frozen; private bookkeeping remains mutable."""
        ...

    def __hash__(self) -> int:
        ...

    def thaw(self) -> DDM:
        """Return a mutable DDM copy of the frozen value object."""
        ...

class IdentityDDM(DDM):
    """Identity-semantic mutable DDM.

    ``IdentityDDM`` provides ordinary DDM mutability with object-identity equality and hashing.

    When to use it
    --------------
    Use when mutable records must be stored in built-in sets or used as dict keys by identity.
    """

    def __hash__(self) -> int:
        ...

class PackedDDM(Mapping[str, Any]):
    """Packed read-heavy DDM.

    ``PackedDDM`` provides slot-backed mapping storage intended to reduce per-instance overhead in large record pools.

    When to use it
    --------------
    Use when many similarly shaped records are mostly read rather than dynamically extended.

    Trade-off
    ---------
    PackedDDM avoids a normal per-instance ``__dict__`` and is intended for large, read-heavy record pools. It deliberately gives up some of ordinary DDM's dynamic attribute-storage flexibility in exchange for lower overhead.
    """

    def __init__(self, data: Mapping[str, Any], *, intern_keys: bool=True) -> None:
        """Initialize a new PackedDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        intern_keys : bool (default: ``True``)
            Whether repeated string keys should be interned to reduce memory overhead.
        """
        ...

    @property
    def _native_data(self) -> Dict[str, Any]:
        ...

    @property
    def _data(self) -> Dict[str, Any]:
        ...

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Recursively serialize the object into ordinary Python containers suitable for JSON-compatible processing.

        Returns
        -------
        Recursively converted ordinary Python dictionary.

        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        ...

    def to_json(self, indent: int=2) -> str:
        """Serialize the object to a JSON string using YoungLion's native JSON encoder.

        Parameters
        ----------
        indent : int (default: ``2``)
            JSON indentation level; use the supported compact value for minimal output.

        Returns
        -------
        JSON text representation.

        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
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
        """
        ...

    @overload
    def get_path(self, path: str, default: T) -> Any | T:
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

        Raises
        ------
        TypeError/ValueError
            If the operation violates PackedDDM mutability/path constraints.

        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
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

    def clone(self) -> PackedDDM:
        """Create an independent deep clone while preserving supported DDM subclass semantics.

        Returns
        -------
        Independent object of the same supported DDM/subclass type.

        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        ...

    def copy(self) -> PackedDDM:
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
        """
        ...

    def memory_info(self, recursive: bool=True) -> _DDMMemoryInfo:
        """Return approximate storage metrics useful for comparing data representations.

        Parameters
        ----------
        recursive : bool (default: ``True``)
            Value supplied for ``recursive`` according to the PackedDDM contract.
        """
        ...

    def freeze(self) -> FrozenDDM:
        """Return an immutable FrozenDDM representation of the current packed data."""
        ...

    def __repr__(self) -> str:
        ...

    def __getattr__(self, name: str) -> Any:
        ...

    def __setattr__(self, name: str, value: Any) -> None:
        ...
    copy = clone

class SchemaDDM(DDM):
    """Schema-validating DDM.

    ``SchemaDDM`` provides runtime schema validation during construction and validated path assignment.

    When to use it
    --------------
    Use at trust boundaries where malformed structured input must be rejected early.
    """

    def __init__(self, data: Mapping[str, Any], schema: Mapping[str, Any], *, strict: bool=True) -> None:
        """Initialize a new SchemaDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        schema : Mapping[str, Any]
            Schema mapping describing expected fields/types/constraints.
        strict : bool (default: ``True``)
            Whether validation rejects fields/conditions beyond the schema contract.
        """
        ...

    def validate(self) -> _SchemaValidation:
        """Validate current state against the configured schema."""
        ...

    def set_validated(self, path: str, value: Any) -> SchemaDDM:
        """Assign a dotted-path value only if the resulting SchemaDDM remains valid.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        """
        ...

class DefaultDDM(DDM):
    """Default-producing DDM.

    ``DefaultDDM`` provides top-level missing keys and attributes resolved through a default factory.

    When to use it
    --------------
    Use for sparse settings/state objects where a consistent fallback policy is preferred.
    """

    def __init__(self, data: Mapping[str, Any], default_factory: Callable[[], Any]=...) -> None:
        """Initialize a new DefaultDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        default_factory : Callable[[], Any] (default: ``lambda: None``)
            Callable producing fallback values for missing top-level keys/attributes.
        """
        ...

    def __getitem__(self, key: str) -> Any:
        ...

    def __getattr__(self, name: str) -> Any:
        ...

    def __missing__(self, key: str) -> Any:
        ...

class LazyDDM(DDM):
    """Lazy-field DDM.

    ``LazyDDM`` provides on-demand field computation with per-field caching and invalidation.

    When to use it
    --------------
    Use for derived values that are expensive or unnecessary for every record.
    """

    def __init__(self, data: Mapping[str, Any], lazy: Mapping[str, Callable[[LazyDDM], Any]] | None=None) -> None:
        """Initialize a new LazyDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        lazy : Optional[Mapping[str, Callable[['LazyDDM'], Any]]] (default: ``None``)
            Mapping of field names to callables used for on-demand LazyDDM values.
        """
        ...

    def invalidate(self, *fields: str) -> LazyDDM:
        """Invalidate cached lazy fields so they will be recomputed on next access.

        Parameters
        ----------
        *fields : str
            Field names or field mapping used for structured document data.
        """
        ...

    def __getattr__(self, name: str) -> Any:
        ...

class ViewDDM(Mapping[str, Any]):
    """Zero-copy mapping view.

    ``ViewDDM`` provides DDM-style path operations directly over an externally owned mutable mapping.

    When to use it
    --------------
    Use when copying would be wasteful and shared mutation is explicitly desired.
    """

    def __init__(self, mapping: Dict[str, Any]) -> None:
        """Initialize a new ViewDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        mapping : Dict[str, Any]
            Mapping that supplies source values, rename rules or transformation instructions.
        """
        ...

    @property
    def _native_data(self) -> Dict[str, Any]:
        ...

    @property
    def _data(self) -> Dict[str, Any]:
        ...

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Recursively serialize the object into ordinary Python containers suitable for JSON-compatible processing.

        Returns
        -------
        Recursively converted ordinary Python dictionary.

        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
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
        """
        ...

    @overload
    def get_path(self, path: str, default: T) -> Any | T:
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
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
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

    def __repr__(self) -> str:
        ...

    def __getattr__(self, name: str) -> Any:
        ...
