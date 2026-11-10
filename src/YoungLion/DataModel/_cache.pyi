"""DataModel cache, builder and batch utility helpers.

This module complements DDM with :class:`SmartCache`, a template-driven completion
helper; :class:`DDMBuilder`, a fluent constructor; and convenience functions for
merging, comparing, transforming, filtering, validating and inspecting DDM
objects.  The functions are intentionally small orchestration utilities built on
top of the public DDM contract so they remain easy to compose in scripts and
services.
"""
from typing import TypeVar
TResult = TypeVar('TResult')
from collections.abc import Callable, Iterable, Mapping
from typing import Any, Dict, List
from ._core import DDM, _SchemaValidation

from typing import TypedDict

class _CacheStats(TypedDict):
    """Completion counters and the current number of top-level template fields."""
    completed: int
    filled_keys: int
    template_keys: int

class _CompletionReport(TypedDict):
    """Top-level missing/extra fields before completion; does not mutate counters."""
    missing_keys: list[str]
    extra_keys: list[str]
    complete: bool
    missing_count: int
    extra_count: int

class SmartCache:
    """Template-driven record completion cache.

    ``SmartCache`` provides fast completion of sparse mappings against a reusable template plus completion statistics.

    When to use it
    --------------
    Use when many records should be normalized to a known key structure.
    """
    template: Dict[str, Any]

    def __init__(self, template: Mapping[str, Any]) -> None:
        """Initialize a new SmartCache instance using the supplied configuration and input data.

        Parameters
        ----------
        template : Mapping[str, Any]
            Reference mapping whose keys/default values define the completion shape.
        """
        ...

    def complete(self, raw_data: Mapping[str, Any], recursive: bool=True) -> Dict[str, Any]:
        """Complete one record without mutating raw_data or the template.

        With recursive=True (the default), nested dictionaries are merged using the native completion path. With recursive=False, an input nested value replaces the entire corresponding template value. Returned containers are independent copies. Statistics count completed records and missing top-level template keys.
        """
        ...

    def complete_batch(self, records: Iterable[Mapping[str, Any]], recursive: bool=True) -> List[Dict[str, Any]]:
        """Complete an iterable once and return a list of independent records.

        recursive is forwarded to complete() for each record. The default recursively fills missing dictionary fields; False selects top-level completion. Completion statistics are updated per record.
        """
        ...

    def get_missing_keys(self, raw_data: Mapping[str, Any]) -> List[str]:
        """Return template keys that are absent from the supplied record.

        Parameters
        ----------
        raw_data : Mapping[str, Any]
            Sparse/source mapping to inspect or complete.
        """
        ...

    def get_extra_keys(self, raw_data: Mapping[str, Any]) -> List[str]:
        """Return input keys that are not present in the current template.

        Parameters
        ----------
        raw_data : Mapping[str, Any]
            Sparse/source mapping to inspect or complete.
        """
        ...

    def completion_report(self, raw_data: Mapping[str, Any]) -> _CompletionReport:
        """Describe how a record differs from the template before completion.

        Parameters
        ----------
        raw_data : Mapping[str, Any]
            Sparse/source mapping to inspect or complete.
        """
        ...

    def update_template(self, new_template: Mapping[str, Any]) -> SmartCache:
        """Replace the reusable completion template and refresh internal cache state.

        Parameters
        ----------
        new_template : Mapping[str, Any]
            Value supplied for ``new_template`` according to the SmartCache contract.
        """
        ...

    def get_stats(self) -> _CacheStats:
        """Return current counters/statistics collected by this object."""
        ...

    def reset_stats(self) -> None:
        """Reset accumulated statistics without changing the primary configured data."""
        ...

    def get_template(self) -> Dict[str, Any]:
        """Return a deep independent copy of the current completion template."""
        ...

    def clone_with_template(self, new_template: Mapping[str, Any]) -> 'SmartCache':
        """Create an independent cache with a new template and zero statistics."""
        ...
    fill = complete
    fill_batch = complete_batch
    report = completion_report
SC = SmartCache

class DDMBuilder:
    """Fluent DDM construction helper.

    ``DDMBuilder`` provides chainable setting, nested construction and list assignment.

    When to use it
    --------------
    Use when programmatic construction is clearer as a fluent pipeline than as nested dict literals.
    """

    def __init__(self) -> None:
        """Initialize a new DDMBuilder instance using the supplied configuration and input data."""
        ...

    def set(self, key: str, value: Any) -> DDMBuilder:
        """Add a field assignment to the builder/plan and return self for fluent chaining.

        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        value : Any
            Target, new or comparison value.
        """
        ...

    def set_many(self, **kwargs: Any) -> DDMBuilder:
        """Add several top-level field assignments in one fluent builder call.

        Parameters
        ----------
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        ...

    def nest(self, key: str, builder_func: Callable[[DDMBuilder], Any]) -> DDMBuilder:
        """Create and assign a nested DDM through a child builder callback.

        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        builder_func : Callable[['DDMBuilder'], Any]
            Value supplied for ``builder_func`` according to the DDMBuilder contract.
        """
        ...

    def add_list(self, key: str, values: Iterable[Any]) -> DDMBuilder:
        """Assign a list value through the fluent DDM builder.

        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        values : Iterable[Any]
            Input iterable, mapping values or composite lookup values.
        """
        ...

    def build(self) -> DDM:
        """Materialize and return the DDM represented by the builder state."""
        ...

def merge_ddms(*ddms: DDM) -> DDM:
    """Merge multiple DDM objects into one new DDM using DDM merge semantics in argument order.

    Parameters
    ----------
    *ddms : DDM
        Value supplied for ``ddms`` according to the function contract.
    """
    ...

def compare_ddms(ddm1: DDM, ddm2: DDM) -> Dict[str, Any]:
    """Compare two DDM objects and return a structured summary of equality/differences.

    Parameters
    ----------
    ddm1 : DDM
        Value supplied for ``ddm1`` according to the function contract.
    ddm2 : DDM
        Value supplied for ``ddm2`` according to the function contract.
    """
    ...

def batch_transform(ddms: Iterable[DDM], transformer: Callable[[DDM], TResult]) -> List[TResult]:
    """Apply a transformer callable to every DDM in an iterable and return the transformed batch.

    Parameters
    ----------
    ddms : Iterable[DDM]
        Value supplied for ``ddms`` according to the function contract.
    transformer : Callable[[DDM], Any]
        Value supplied for ``transformer`` according to the function contract.
    """
    ...

def batch_filter(ddms: Iterable[DDM], predicate: Callable[[DDM], bool]) -> List[DDM]:
    """Return only DDM objects for which the predicate evaluates truthfully.

    Parameters
    ----------
    ddms : Iterable[DDM]
        Value supplied for ``ddms`` according to the function contract.
    predicate : Callable[[DDM], bool]
        Callable returning truthy for records that should match/be selected.
    """
    ...

def validate_ddm_batch(ddms: Iterable[DDM], schema: Dict[str, Any]) -> List[_SchemaValidation]:
    """Validate every DDM in a batch against the same schema and return per-item results.

    Parameters
    ----------
    ddms : Iterable[DDM]
        Value supplied for ``ddms`` according to the function contract.
    schema : Dict[str, Any]
        Schema mapping describing expected fields/types/constraints.
    """
    ...

def analyze_ddm_structure(ddm: DDM) -> Dict[str, Any]:
    """Inspect a DDM and return structural information useful for diagnostics and schema understanding.

    Parameters
    ----------
    ddm : DDM
        Value supplied for ``ddm`` according to the function contract.
    """
    ...

def get_ddm_size_info(ddm: DDM) -> Dict[str, int]:
    """Return approximate size/memory metrics for a DDM.

    Parameters
    ----------
    ddm : DDM
        Value supplied for ``ddm`` according to the function contract.
    """
    ...

def create_smart_cache(template: Mapping[str, Any]) -> SmartCache:
    """Construct and return a SmartCache from a completion template.

    Parameters
    ----------
    template : Mapping[str, Any]
        Reference mapping whose keys/default values define the completion shape.
    """
    ...

def fast_complete(template: Mapping[str, Any], raw_data: Mapping[str, Any]) -> Dict[str, Any]:
    """Complete one sparse mapping against a template using a short-lived SmartCache convenience path.

    Parameters
    ----------
    template : Mapping[str, Any]
        Reference mapping whose keys/default values define the completion shape.
    raw_data : Mapping[str, Any]
        Sparse/source mapping to inspect or complete.
    """
    ...

def batch_complete_fast(template: Mapping[str, Any], records: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Complete many sparse mappings against one template using a shared SmartCache.

    Parameters
    ----------
    template : Mapping[str, Any]
        Reference mapping whose keys/default values define the completion shape.
    records : Iterable[Mapping[str, Any]]
        Input records for structured/DDM collection indexing.
    """
    ...

def flatten_to_single_dict(*ddms: DDM) -> Dict[str, Any]:
    """Flatten models into one dictionary with collision-free model prefixes.

    Keys are ``ddm0_profile.name``, ``ddm1_profile.name``, etc. Empty input
    returns {}. Each model uses the usual dotted-path flattening semantics.
    """
    ...
