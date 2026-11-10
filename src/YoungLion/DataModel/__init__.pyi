"""YoungLion.DataModel — dynamic, typed-friendly and high-throughput data modeling.

The DataModel package is the structured-data core of YoungLion.  Its central
abstraction, :class:`DDM` (Dynamic Data Model), keeps JSON-like mappings easy to
inspect and mutate while providing recursive serialization, dotted-path access,
schema validation, cloning, transformations and native C++ accelerated hot paths.

DDM is intentionally subclass-friendly.  Applications can keep the flexibility
of dynamic input while exposing domain-specific attributes such as ``User``,
``UserProfile`` or ``Order`` with normal Python type annotations and methods.
Specialized variants cover immutable values, identity semantics, packed storage,
schema enforcement, default values, lazy fields and zero-copy views.

The package also provides DDM-aware collections for large datasets, builder/cache
utilities and reusable mathematical/data structures such as Range, Vector,
Timeline, Dataset, Size, Point, Color, Matrix and TreeDDM.

Recommended discovery path
--------------------------
1. Start with :class:`DDM` for ordinary hierarchical application data.
2. Subclass DDM for domain models when IDE-visible typed attributes are useful.
3. Use ListDDM/DictDDM/SetDDM and BatchPlan for high-volume operations.
4. Choose a specialized DDM variant only when its semantic trade-off is needed.
5. Pair large collections with :class:`YoungLion.DDMSearchEngine` for reusable
   dotted-path indexes.

All public APIs are documented in their runtime docstrings so ``help()``, IDLE,
interactive shells and IDE hovers remain useful without opening external docs.
"""
from ._core import DDM as DDM
from ._variants import FrozenDDM as FrozenDDM, IdentityDDM as IdentityDDM, PackedDDM as PackedDDM, SchemaDDM as SchemaDDM, DefaultDDM as DefaultDDM, LazyDDM as LazyDDM, ViewDDM as ViewDDM
from ._collections import ListDDM as ListDDM, SetDDM as SetDDM, DictDDM as DictDDM, DDMTable as DDMTable, DDMCollectionOps as DDMCollectionOps, BatchPlan as BatchPlan
from ._models import Range as Range, Vector as Vector, Timeline as Timeline, Dataset as Dataset, Size as Size, Point as Point, Color as Color, Matrix as Matrix, TreeDDM as TreeDDM
from ._cache import SmartCache as SmartCache, SC as SC, DDMBuilder as DDMBuilder, merge_ddms as merge_ddms, compare_ddms as compare_ddms, batch_transform as batch_transform, batch_filter as batch_filter, validate_ddm_batch as validate_ddm_batch, analyze_ddm_structure as analyze_ddm_structure, get_ddm_size_info as get_ddm_size_info, create_smart_cache as create_smart_cache, fast_complete as fast_complete, batch_complete_fast as batch_complete_fast

from ._cache import flatten_to_single_dict as flatten_to_single_dict
from ._parsing import ParseError as ParseError, split_any as split_any, ensure_int_list as ensure_int_list, enable_ansi as enable_ansi
