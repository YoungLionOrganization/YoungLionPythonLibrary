"""High-throughput DDM-aware collection types and bulk algorithms.

This module provides ListDDM, SetDDM, DictDDM and DDMTable together with the
shared :class:`DDMCollectionOps` operation surface.  The collection layer is
optimized for workloads containing many DDM-compatible records and supports
native dotted-path extraction, filtering, numeric transforms/reductions,
partitioning, stable sorting, binary-search style algorithms, grouping,
deduplication, chunking and search-index construction.

:class:`BatchPlan` is the preferred tool when several simple mutations must be
applied to every record.  It compiles a sequence of set/add/subtract/multiply/
divide/clamp operations and lets the native extension execute them in one pass,
reducing repeated Python-to-native traversal overhead.

These classes intentionally resemble built-in collections where practical while
adding record-oriented operations that ordinary list/set/dict types do not
provide.  Operations that mutate records invalidate cached search indexes so
callers do not accidentally query stale collection-managed indexes.
"""
TDefault = TypeVar('TDefault')
from collections.abc import ItemsView, ValuesView
TCollection = TypeVar('TCollection', bound='DDMCollectionOps[Any]')
TResult = TypeVar('TResult')
if TYPE_CHECKING:
    from ..search import DDMSearchEngine
from typing import Literal, TYPE_CHECKING
from collections import Counter
from collections.abc import Callable, Hashable, Iterable, Iterator, Mapping, MutableMapping, MutableSequence, Sequence
from typing import Any, Generic, TypeVar, overload
from ._core import DDM
TItem = TypeVar('TItem', bound=Any)
K = TypeVar('K', bound=Hashable)

class BatchPlan:
    """Compiled bulk mutation plan.

    ``BatchPlan`` provides multiple simple dotted-path mutations executed in a single native collection pass.

    When to use it
    --------------
    Use when applying several arithmetic/set operations to every record in a large collection.
    """

    def __init__(self) -> None:
        """Initialize a new BatchPlan instance using the supplied configuration and input data."""
        ...

    def set(self, path: str, value: Any) -> BatchPlan:
        """Add a field assignment to the builder/plan and return self for fluent chaining.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def add(self, path: str, amount: float=1.0) -> BatchPlan:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        amount : float (default: ``1.0``)
            Numeric amount to add or subtract.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def subtract(self, path: str, amount: float=1.0) -> BatchPlan:
        """Subtract another value or queue a subtraction operation.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        amount : float (default: ``1.0``)
            Numeric amount to add or subtract.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...
    sub = subtract

    def multiply(self, path: str, factor: float) -> BatchPlan:
        """Multiply the addressed numeric values by a factor.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        factor : float
            Numeric scaling/multiplication factor.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...
    mul = multiply

    def divide(self, path: str, divisor: float) -> BatchPlan:
        """Divide the addressed numeric values by a divisor.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        divisor : float
            Numeric divisor; zero is invalid.


        Raises
        ------
        ZeroDivisionError/ValueError
            If the supplied divisor is zero, according to the native/Python operation path.

        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...
    div = divide

    def clamp(self, path: str, minimum: float, maximum: float) -> BatchPlan:
        """Constrain a value or all addressed numeric values to the supplied inclusive bounds.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        minimum : float
            Lower bound or minimum accepted value.
        maximum : float
            Upper bound or maximum accepted value.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def clear(self) -> BatchPlan:
        """Remove all currently stored entries or queued operations, depending on the owning class.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def execute(self, collection: DDMCollectionOps[Any]) -> int:
        """Execute the queued batch plan against a DDM-aware collection.

        Parameters
        ----------
        collection : Any
            Value supplied for ``collection`` according to the BatchPlan contract.


        Notes
        -----
        Queued operations are passed to the native collection routine together so each record can be visited once. This is most beneficial when several simple path mutations would otherwise require repeated full scans.
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def __len__(self) -> int:
        ...

class DDMCollectionOps(Generic[TItem]):
    """Shared DDM collection operation surface.

    ``DDMCollectionOps`` provides bulk path access, transforms, reductions, algorithms and search integration.

    When to use it
    --------------
    Inherited by ListDDM/SetDDM/DictDDM/DDMTable; normally use those concrete containers.
    """

    def batch(self) -> BatchPlan:
        """Return a new BatchPlan for composing several one-pass mutations.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def path_values(self, path: str, default: Any=None) -> list[Any]:
        """Extract the value at the same dotted path from every collection record.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...
    pluck = path_values

    def set_all(self, path: str, value: Any) -> int:
        """Set one dotted path to the same value across every collection record.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def apply_path(self, path: str, func: Callable[[Any], Any], *, write_back: bool=True) -> list[Any]:
        """Apply a callable to a dotted-path value for each record, optionally writing transformed values back.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        func : Callable[[Any], Any]
            Callable applied by the operation.
        write_back : bool (default: ``True``)
            When True, store transformed values back into records; otherwise only return results.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def map(self, func: Callable[[TItem], TResult]) -> list[TResult]:
        """Apply a callable to every record and return the mapped results.

        Parameters
        ----------
        func : Callable[[Any], Any]
            Callable applied by the operation.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def for_each(self: TCollection, func: Callable[[TItem], Any]) -> TCollection:
        """Invoke a callable for every record for side effects.

        Parameters
        ----------
        func : Callable[[Any], Any]
            Callable applied by the operation.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def reduce(self, func: Callable[[Any, TItem], Any], initial: Any=...) -> Any:
        """Fold the collection into one accumulated value.

        Parameters
        ----------
        func : Callable[[Any, Any], Any]
            Callable applied by the operation.
        initial : Any (default: ``_MISSING``)
            Initial accumulator value for reduction.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def filter(self, predicate: Callable[[TItem], bool]) -> list[TItem]:
        """Return records for which the supplied predicate evaluates truthfully.

        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.

        Returns
        -------
        Collection/list of matching records without modifying non-inplace source state.

        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def filter_path(self, path: str, value: Any=None, *, op: str='eq') -> list[TItem]:
        """Filter records by comparing a dotted-path value with a target using the selected operator.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.

        Example::

            adults = users.filter_path("profile.age", 18, op="gte")
        """
        ...
    where = filter_path

    @overload
    def first(self, predicate: Callable[[TItem], bool] | None=None, default: None=None) -> TItem | None:
        """Return the first record satisfying a predicate or a caller-provided default.

        Parameters
        ----------
        predicate : Optional[Callable[[Any], bool]] (default: ``None``)
            Callable returning truthy for records that should match/be selected.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def first(self, predicate: Callable[[TItem], bool] | None, default: TDefault) -> TItem | TDefault:
        """Return the first record satisfying a predicate or a caller-provided default.

        Parameters
        ----------
        predicate : Optional[Callable[[Any], bool]] (default: ``None``)
            Callable returning truthy for records that should match/be selected.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def first(self, predicate: Callable[[TItem], bool] | None = None, *, default: TDefault) -> TItem | TDefault:
        """Return the first matching record or an explicitly supplied keyword default."""
        ...

    @overload
    def first_path(self, path: str, value: Any=None, *, op: str='eq', default: None=None) -> TItem | None:
        """Return the first record whose dotted-path value satisfies the requested comparison.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def first_path(self, path: str, value: Any=None, *, op: str='eq', default: TDefault) -> TItem | TDefault:
        """Return the first record whose dotted-path value satisfies the requested comparison.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def any(self, predicate: Callable[[TItem], bool]) -> bool:
        """Return whether at least one record satisfies the predicate.

        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def all(self, predicate: Callable[[TItem], bool]) -> bool:
        """Return whether every record satisfies the predicate.

        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def exists_path(self, path: str, value: Any=None, *, op: str='eq') -> bool:
        """Return whether any record satisfies a dotted-path comparison.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def count_path(self, path: str, value: Any=None, *, op: str='eq') -> int:
        """Count records satisfying a dotted-path comparison without allocating a result list.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def partition_path(self, path: str, value: Any=None, *, op: str='eq') -> tuple[list[TItem], list[TItem]]:
        """Split records into matching and non-matching groups using a dotted-path comparison.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def update_all(self, **values: Any) -> int:
        """Apply the supplied top-level assignments to every collection record.

        Parameters
        ----------
        **values : Any
            Input iterable, mapping values or composite lookup values.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def update_where(self, predicate: Callable[[TItem], bool], **values: Any) -> int:
        """Update only records satisfying the supplied Python predicate.

        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.
        **values : Any
            Input iterable, mapping values or composite lookup values.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def apply_where(self, predicate: Callable[[TItem], bool], path: str, func: Callable[[Any], Any]) -> int:
        """Transform one dotted-path value only on records satisfying a predicate.

        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.
        path : str
            Filesystem path or dotted data path, according to the owning API.
        func : Callable[[Any], Any]
            Callable applied by the operation.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def increment(self, path: str, amount: float=1.0) -> int:
        """Add an amount to the addressed numeric value in every record.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        amount : float (default: ``1.0``)
            Numeric amount to add or subtract.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.

        Example::

            users.increment("economy.balance", 25)
        """
        ...

    def decrement(self, path: str, amount: float=1.0) -> int:
        """Subtract an amount from the addressed numeric value in every record.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        amount : float (default: ``1.0``)
            Numeric amount to add or subtract.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def multiply(self, path: str, factor: float) -> int:
        """Multiply the addressed numeric values by a factor.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        factor : float
            Numeric scaling/multiplication factor.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def divide(self, path: str, divisor: float) -> int:
        """Divide the addressed numeric values by a divisor.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        divisor : float
            Numeric divisor; zero is invalid.


        Raises
        ------
        ZeroDivisionError/ValueError
            If the supplied divisor is zero, according to the native/Python operation path.

        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def clamp(self, path: str, minimum: float, maximum: float) -> int:
        """Constrain a value or all addressed numeric values to the supplied inclusive bounds.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        minimum : float
            Lower bound or minimum accepted value.
        maximum : float
            Upper bound or maximum accepted value.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def sum(self, path: str) -> float:
        """Return the numeric sum of values found at the requested dotted path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def mean(self, path: str) -> float | None:
        """Return the arithmetic mean of numeric values found at the requested dotted path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def min(self, path: str) -> float | None:
        """Return the minimum numeric value found at the requested dotted path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def max(self, path: str) -> float | None:
        """Return the maximum numeric value found at the requested dotted path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def numeric_count(self, path: str) -> int:
        """Count records containing numeric data at the requested dotted path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def sort_by(self, path: str, *, reverse: bool=False, missing_last: bool=True, inplace: Literal[False]=False) -> list[TItem]:
        """Sort records by a column/dotted path with explicit missing-value and in-place behavior.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        missing_last : bool (default: ``True``)
            Whether records lacking the sort path should be placed after records with values.
        inplace : bool (default: ``False``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def sort_by(self: TCollection, path: str, *, reverse: bool=False, missing_last: bool=True, inplace: Literal[True]=True) -> TCollection:
        """Sort records by a column/dotted path with explicit missing-value and in-place behavior.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        missing_last : bool (default: ``True``)
            Whether records lacking the sort path should be placed after records with values.
        inplace : bool (default: ``False``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def sort_by(self: TCollection, path: str, *, reverse: bool=False, missing_last: bool=True, inplace: bool) -> list[TItem] | TCollection:
        """Sort records by a column/dotted path with explicit missing-value and in-place behavior.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        missing_last : bool (default: ``True``)
            Whether records lacking the sort path should be placed after records with values.
        inplace : bool (default: ``False``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def is_sorted(self, path: str, *, reverse: bool=False) -> bool:
        """Check whether records are already ordered by the requested dotted path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def lower_bound(self, path: str, value: Any, *, reverse: bool=False, verify_sorted: bool=True) -> int:
        """Return the insertion boundary for a value in records sorted by the requested path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        verify_sorted : bool (default: ``True``)
            Whether to validate sorted-order preconditions before a binary-search style operation.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def equal_range(self, path: str, value: Any, *, reverse: bool=False, verify_sorted: bool=True) -> tuple[int, int]:
        """Return the half-open range of positions containing values equal to the target in sorted records.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        verify_sorted : bool (default: ``True``)
            Whether to validate sorted-order preconditions before a binary-search style operation.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def binary_search(self, path: str, value: Any, *, reverse: bool=False, verify_sorted: bool=True) -> int:
        """Locate a target value in records sorted by the requested dotted path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        verify_sorted : bool (default: ``True``)
            Whether to validate sorted-order preconditions before a binary-search style operation.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def nth(self, path: str, n: int, *, largest: bool=False) -> TItem:
        """Select the record at an order-statistic position without requiring a full Python-side sort.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        n : int
            Requested count, rank or n-gram width depending on the API.
        largest : bool (default: ``False``)
            Whether order-statistic selection counts from the largest side.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def top(self, path: str, n: int=10, *, largest: bool=True) -> list[TItem]:
        """Return the highest-ranked records for a dotted-path value.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        n : int (default: ``10``)
            Requested count, rank or n-gram width depending on the API.
        largest : bool (default: ``True``)
            Whether order-statistic selection counts from the largest side.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def bottom(self, path: str, n: int=10) -> list[TItem]:
        """Return the lowest-ranked records for a dotted-path value.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        n : int (default: ``10``)
            Requested count, rank or n-gram width depending on the API.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def group_by(self, path: str, default: Any=None) -> dict[Any, list[TItem]]:
        """Group records or values by the requested field/callback and return the resulting buckets.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def count_by(self, path: str, default: Any=None) -> Counter[Any]:
        """Count records per distinct dotted-path value.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def distinct(self, path: str, default: Any=None) -> list[Any]:
        """Return distinct values observed at a dotted path while preserving supported collection semantics.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def deduplicate(self, path: str | None=None, *, inplace: Literal[False]=False) -> list[TItem]:
        """Remove duplicate records/keys according to a dotted path.

        Parameters
        ----------
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.
        inplace : bool (default: ``False``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def deduplicate(self: TCollection, path: str | None=None, *, inplace: Literal[True]=True) -> TCollection:
        """Remove duplicate records/keys according to a dotted path.

        Parameters
        ----------
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.
        inplace : bool (default: ``False``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def deduplicate(self: TCollection, path: str | None=None, *, inplace: bool) -> list[TItem] | TCollection:
        """Remove duplicate records/keys according to a dotted path.

        Parameters
        ----------
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.
        inplace : bool (default: ``False``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def partition(self, predicate: Callable[[TItem], bool]) -> tuple[list[TItem], list[TItem]]:
        """Split the collection into records that do and do not satisfy a predicate.

        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def chunks(self, size: int) -> Iterator[list[TItem]]:
        """Yield or return bounded-size chunks of the collection for incremental processing.

        Parameters
        ----------
        size : int
            Requested size/dimension/chunk width.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def take(self, count: int) -> list[TItem]:
        """Return the first requested number of records.

        Parameters
        ----------
        count : int
            Requested number of records/items.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def skip(self, count: int) -> list[TItem]:
        """Return records after skipping the requested leading count.

        Parameters
        ----------
        count : int
            Requested number of records/items.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def sample(self, count: int) -> list[TItem]:
        """Return a random sample without requiring callers to manipulate backing storage directly.

        Parameters
        ----------
        count : int
            Requested number of records/items.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def shuffle(self: TCollection, *, inplace: Literal[True]=True) -> TCollection:
        """Randomize record order, optionally mutating the collection.

        Parameters
        ----------
        inplace : bool (default: ``True``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def shuffle(self, *, inplace: Literal[False]=False) -> list[TItem]:
        """Randomize record order, optionally mutating the collection.

        Parameters
        ----------
        inplace : bool (default: ``True``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def shuffle(self: TCollection, *, inplace: bool) -> list[TItem] | TCollection:
        """Randomize record order, optionally mutating the collection.

        Parameters
        ----------
        inplace : bool (default: ``True``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def reverse(self: TCollection, *, inplace: Literal[True]=True) -> TCollection:
        """Reverse record/event order, optionally mutating according to the class contract.

        Parameters
        ----------
        inplace : bool (default: ``True``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def reverse(self, *, inplace: Literal[False]=False) -> list[TItem]:
        """Reverse record/event order, optionally mutating according to the class contract.

        Parameters
        ----------
        inplace : bool (default: ``True``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    @overload
    def reverse(self: TCollection, *, inplace: bool) -> list[TItem] | TCollection:
        """Reverse record/event order, optionally mutating according to the class contract.

        Parameters
        ----------
        inplace : bool (default: ``True``)
            When True, mutate/reorder the collection itself where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def rename_path(self, old_path: str, new_path: str, *, missing: Any=...) -> int:
        """Move a value from one dotted path to another name/path across records.

        Parameters
        ----------
        old_path : str
            Existing filesystem or dotted-data path to move/rename from.
        new_path : str
            Destination filesystem or dotted-data path to move/rename to.
        missing : Any (default: ``_MISSING``)
            Fallback/behavior used when the source dotted path does not exist.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def copy_path(self, source: str, destination: str, *, missing: Any=...) -> int:
        """Copy a value from one dotted path to another across records.

        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        missing : Any (default: ``_MISSING``)
            Fallback/behavior used when the source dotted path does not exist.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def move_path(self, source: str, destination: str, *, missing: Any=...) -> int:
        """Move a value from one dotted path to another across records and remove the source.

        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        missing : Any (default: ``_MISSING``)
            Fallback/behavior used when the source dotted path does not exist.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def fill_missing(self, path: str, value: Any) -> int:
        """Populate a dotted path only when that path is missing.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def delete_path(self, path: str) -> int:
        """Delete a dotted path from every record where it exists.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def search(self, path: str, value: Any=None, *, op: str='eq', limit: int | None=None, use_index: bool=True) -> list[TItem]:
        """Find records matching a dotted path and value.

        Parameters
        ----------
        path : str
            Nested data path such as profile.name.
        value : Any
            Comparison value; ignored by existence operators.
        op : str
            Supported comparison operator, such as eq, ne, lt, contains.
        limit : int | None
            Maximum results; None returns every matching record.
        use_index : bool
            Use an available index when True; otherwise scan.

        Returns
        -------
        A list containing references to the original matching records. Uses the cached collection search engine when available. External mutations require refresh/invalidation as documented for DDMSearchEngine.
        """
        ...

    def build_search_index(self, *paths: str, **kwargs: Any) -> DDMSearchEngine:
        """Build and return a reusable DDMSearchEngine over this collection.

        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

class ListDDM(DDMCollectionOps[DDM], MutableSequence[DDM]):  # type: ignore[misc]  # reverse() intentionally returns self for chaining.
    """Sequence-oriented DDM collection.

    ``ListDDM`` provides mutable list semantics plus high-throughput DDM bulk/path operations.

    When to use it
    --------------
    Use when record order and duplicate records are meaningful.
    """

    def __init__(self, values: Iterable[DDM | Mapping[str, Any]]=()) -> None:
        """Initialize a new ListDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        values : Iterable[Any] (default: ``()``)
            Input iterable, mapping values or composite lookup values.
        """
        ...

    def __len__(self) -> int:
        ...

    @overload
    def __getitem__(self, index: int) -> DDM:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[DDM]:
        ...

    @overload
    def __setitem__(self, index: int, value: DDM | Mapping[str, Any]) -> None:
        ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[DDM | Mapping[str, Any]]) -> None:
        ...

    def __delitem__(self, index: int | slice) -> None:
        ...

    def insert(self, index: int, value: DDM | Mapping[str, Any]) -> None:
        """Insert a record at the requested sequence position.

        Parameters
        ----------
        index : int
            Value supplied for ``index`` according to the ListDDM contract.
        value : Any
            Target, new or comparison value.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def __iter__(self) -> Iterator[DDM]:
        ...

    def indexed(self, *paths: str, **kwargs: Any) -> DDMSearchEngine:
        """Build or reuse a DDMSearchEngine with indexes for the requested paths.

        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def __repr__(self) -> str:
        ...

class SetDDM(DDMCollectionOps[DDM]):
    """Uniqueness-oriented DDM collection.

    ``SetDDM`` provides ordered record storage with configurable stable uniqueness keys.

    When to use it
    --------------
    Prefer key_path for large mutable datasets with a stable primary key; call rehash after external key mutations.

    Uniqueness semantics
    --------------------
    Ordinary mutable DDM uses value equality and is intentionally unhashable. SetDDM therefore maintains its own stable uniqueness keys. For large datasets prefer ``key_path`` pointing to an immutable primary-key field; use ``rehash()`` after direct external mutations that change the uniqueness key.
    """

    def __init__(self, values: Iterable[DDM | Mapping[str, Any]]=(), *, key: Callable[[DDM], Hashable] | None=None, key_path: str | None=None) -> None:
        """Initialize a new SetDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        values : Iterable[Any] (default: ``()``)
            Input iterable, mapping values or composite lookup values.
        key : Optional[Callable[[Any], Hashable]] (default: ``None``)
            Mapping key or uniqueness key.
        key_path : Optional[str] (default: ``None``)
            Dotted path used as a stable uniqueness key for SetDDM.
        """
        ...

    def add(self, value: DDM | Mapping[str, Any]) -> bool:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        value : Any
            Target, new or comparison value.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def discard(self, value: DDM | Mapping[str, Any]) -> bool:
        """Remove a set-like record if present without raising for absence.

        Parameters
        ----------
        value : Any
            Target, new or comparison value.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def remove(self, value: DDM | Mapping[str, Any]) -> None:
        """Remove an existing record/document/event and raise or report according to the class contract when absent.

        Parameters
        ----------
        value : Any
            Target, new or comparison value.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def __contains__(self, value: object) -> bool:
        ...

    def __iter__(self) -> Iterator[DDM]:
        ...

    def __len__(self) -> int:
        ...

    def rehash(self) -> SetDDM:
        """Rebuild SetDDM uniqueness keys after external mutation of stored records.


        Notes
        -----
        Call this after directly mutating values that participate in SetDDM uniqueness. Collection-provided mutation methods already refresh internal uniqueness/search state where applicable.
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def __repr__(self) -> str:
        ...

class DictDDM(DDMCollectionOps[DDM], MutableMapping[K, DDM], Generic[K]):
    """Keyed DDM collection.

    ``DictDDM`` provides application-defined mapping keys whose values participate in DDM bulk/search operations.

    When to use it
    --------------
    Use for registries, entity maps and caches where external keys must be retained.
    """

    def __init__(self, values: Mapping[K, DDM | Mapping[str, Any]] | None=None, **kwargs: Any) -> None:
        """Initialize a new DictDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        values : Optional[Mapping[K, Any]] (default: ``None``)
            Input iterable, mapping values or composite lookup values.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        ...

    def __getitem__(self, key: K) -> DDM:
        ...

    def __setitem__(self, key: K, value: DDM | Mapping[str, Any]) -> None:
        ...

    def __delitem__(self, key: K) -> None:
        ...

    def __iter__(self) -> Iterator[K]:
        ...

    def __len__(self) -> int:
        ...

    def values(self) -> ValuesView[DDM]:
        """Return a dynamic view or collection of stored values.

        Returns
        -------
        Result collection/value produced by the operation.

        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def items(self) -> ItemsView[K, DDM]:
        """Return key/value pairs for the current mapping-like object.

        Returns
        -------
        Result collection/value produced by the operation.

        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def keys_for(self, path: str, value: Any=None, *, op: str='eq') -> list[K]:
        """Return DictDDM mapping keys whose values satisfy a dotted-path comparison.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def indexed(self, *paths: str, **kwargs: Any) -> DDMSearchEngine:
        """Build or reuse a DDMSearchEngine with indexes for the requested paths.

        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def __repr__(self) -> str:
        ...

class DDMTable(ListDDM):
    """Lightweight structured table.

    ``DDMTable`` provides ListDDM operations plus column selection, assignment and criteria queries.

    When to use it
    --------------
    Use for small/medium zero-dependency tabular workflows; it is not a pandas replacement.
    """

    def columns(self) -> list[str]:
        """Return the column names observed in the table records.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def select(self, *paths: str) -> list[dict[str, Any]]:
        """Project table rows to the requested dotted-path columns.

        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def assign(self, **path_values: Any) -> DDMTable:
        """Assign one or more columns/dotted paths across the table.

        Parameters
        ----------
        **path_values : Any
            Value supplied for ``path_values`` according to the DDMTable contract.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...

    def query(self, **criteria: Any) -> DDMTable:
        """Execute a class-specific query and return matching values/results.

        Parameters
        ----------
        **criteria : Any
            Value supplied for ``criteria`` according to the DDMTable contract.


        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ...
