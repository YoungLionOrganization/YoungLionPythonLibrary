"""C++17 extension contracts. Functions without keyword support use positional-only parameters. Public Python wrappers provide the ergonomic API. No runtime third-party dependencies."""
from collections.abc import Callable, Mapping, Sequence
from typing import Any

def json_dumps(obj: Any, indent: int=2) -> str:
    """Native JSON serializer.

    Accepts the named keyword parameters shown in the signature.
    """
    ...

def json_loads(data: str, /) -> Any:
    """Native JSON parser.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ddm_to_dict(obj: Any, /) -> dict[str, Any]:
    """Serialize public attributes.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ddm_clone_data(obj: Any, /) -> dict[str, Any]:
    """Deep-copy public DDM data.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ddm_get_path(obj: Any, path: str, default: Any=None, /) -> Any:
    """Get dotted path.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ddm_set_path(obj: Any, path: str, value: Any, /) -> bool:
    """Set dotted path.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ddm_has_path(obj: Any, path: str, /) -> bool:
    """Check dotted path.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ddm_merge_data(obj: Any, other: Any, /) -> dict[str, Any]:
    """Native deep merge.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ddm_diff(a: Any, b: Any, /) -> dict[str, Any]:
    """Native DDM diff.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ddm_flatten(obj: Any, prefix: str='', separator: str='.') -> dict[str, Any]:
    """Flatten nested data.

    Accepts the named keyword parameters shown in the signature.
    """
    ...

def ddm_validate_schema(obj: Any, schema: Mapping[str, Any], /) -> dict[str, Any]:
    """Validate simple schema.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ddm_memory_info(obj: Any, recursive: bool=True, /) -> dict[str, int]:
    """Measure DDM memory usage.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def cache_complete(template: Mapping[str, Any], data: Mapping[str, Any], /) -> dict[str, Any]:
    """Fast template completion.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def cache_missing(template: Mapping[str, Any], data: Mapping[str, Any], /) -> list[str]:
    """Missing keys.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def cache_extra(template: Mapping[str, Any], data: Mapping[str, Any], /) -> list[str]:
    """Extra keys.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def vec_magnitude(values: Sequence[float], /) -> float:
    """Vector magnitude.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def vec_dot(a: Sequence[float], b: Sequence[float], /) -> float:
    """Dot product.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def vec_add(a: Sequence[float], b: Sequence[float], /) -> list[float]:
    """Vector add.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def vec_sub(a: Sequence[float], b: Sequence[float], /) -> list[float]:
    """Vector subtract.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def vec_scale(a: Sequence[float], scalar: float, /) -> list[float]:
    """Vector scale.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def vec_cross(a: Sequence[float], b: Sequence[float], /) -> list[float]:
    """Cross product.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def resolve_path(root: str, path: str, create_parent: bool=True, /) -> str:
    """Resolve file path.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def get_info(path: str, /) -> dict[str, Any]:
    """Get filesystem info.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def list_dir(path: str, /) -> list[str]:
    """List directory.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def create_dir(path: str, /) -> bool:
    """Create directory.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def remove_path(path: str, recursive: bool=False, /) -> bool:
    """Remove file/folder.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def rename_path(source: str, destination: str, /) -> bool:
    """Rename path.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def copy_path(source: str, destination: str, recursive: bool=False, /) -> bool:
    """Copy path.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def move_path(source: str, destination: str, /) -> bool:
    """Move path.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def read_text(path: str, /) -> str:
    """Read UTF-8 text.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def write_text(path: str, content: str, append: bool=False, /) -> None:
    """Write UTF-8 text.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def read_bytes(path: str, /) -> bytes:
    """Read binary file.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def write_bytes(path: str, data: bytes, append: bool=False, /) -> None:
    """Write binary file.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def json_read_file(path: str, /) -> Any:
    """Read JSON file.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def json_write_file(path: str, data: Any, indent: int=4, /) -> None:
    """Write JSON file.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def csv_read(path: str, delimiter: str=',', quotechar: str='"', /) -> list[dict[str, str]]:
    """Read CSV.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def csv_write(path: str, data: list[dict[str, str]], fieldnames: list[str] | None=None, delimiter: str=',', quotechar: str='"', append: bool=False) -> None:
    """Write CSV.

    Accepts the named keyword parameters shown in the signature.
    """
    ...

def properties_read(path: str, /) -> dict[str, str]:
    """Read properties.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def properties_write(path: str, data: Mapping[str, str], append: bool=False, /) -> None:
    """Write properties.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ini_read(path: str, /) -> dict[str, dict[str, str]]:
    """Read INI.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def ini_write(path: str, data: Mapping[str, Mapping[str, str]], append: bool=False, /) -> None:
    """Write INI.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def pdf_write(path: str, content: str, /) -> None:
    """Write dependency-free simple PDF.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def pdf_read(path: str, /) -> str:
    """Best-effort PDF text extraction.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def file_crc32(path: str, /) -> str:
    """CRC32 checksum.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def directory_size(path: str, recursive: bool=True, /) -> int:
    """Directory byte size.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def touch(path: str, /) -> bool:
    """Create or touch a file.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def line_count(path: str, /) -> int:
    """Count text lines.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def compare_files(a: str, b: str, /) -> bool:
    """Binary file comparison.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def levenshtein(a: str, b: str, /) -> int:
    """Unicode Levenshtein distance.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def damerau_levenshtein(a: str, b: str, /) -> int:
    """Unicode Damerau-Levenshtein distance.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def jaro_winkler(a: str, b: str, prefix_scale: float=0.1, /) -> float:
    """Unicode Jaro-Winkler similarity.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def trigram_similarity(a: str, b: str, /) -> float:
    """Unicode trigram Dice similarity.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def find_all(haystack: str, needle: str, /) -> list[int]:
    """Boyer-Moore-Horspool style substring positions.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def bm25_scores(query_tokens: Sequence[str], documents: Sequence[Sequence[str]], k1: float=1.5, b: float=0.75, /) -> list[float]:
    """BM25 document scores.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_get_path(items: Sequence[Any], path: str, default: Any=None, /) -> list[Any]:
    """Extract a dotted path from a DDM batch.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_set_path(items: Sequence[Any], path: str, value: Any, /) -> int:
    """Set a dotted path across a DDM batch.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_apply_path(items: Sequence[Any], path: str, func: Callable[[Any], Any], write_back: bool=True) -> list[Any]:
    """Apply a callable to a dotted path across a DDM batch.

    Accepts the named keyword parameters shown in the signature.
    """
    ...

def batch_filter_path(items: Sequence[Any], path: str, op: str, expected: Any=None, /) -> list[Any]:
    """Filter a DDM batch by a dotted-path comparison.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_count_path(items: Sequence[Any], path: str, op: str, expected: Any=None, /) -> int:
    """Count DDM path matches without allocating a result list.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_partition_path(items: Sequence[Any], path: str, op: str, expected: Any=None, /) -> tuple[list[Any], list[Any]]:
    """Stable partition of DDM records by dotted-path comparison.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_numeric_op(items: Sequence[Any], path: str, op: str, a: float, b: float=0.0, /) -> int:
    """Apply a native numeric operation across a DDM path.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_numeric_reduce(items: Sequence[Any], path: str, op: str, /) -> float | None:
    """Reduce numeric DDM path values in C++.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_sort_path(items: Sequence[Any], path: str, reverse: bool=False, missing_last: bool=True) -> list[Any]:
    """Stable-sort a DDM batch by dotted path.

    Accepts the named keyword parameters shown in the signature.
    """
    ...

def batch_is_sorted_path(items: Sequence[Any], path: str, reverse: bool=False, /) -> bool:
    """Check sorted order using a DDM path.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_lower_bound_path(items: Sequence[Any], path: str, target: Any, reverse: bool=False, /) -> int:
    """C++ lower_bound over a path-sorted DDM batch.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_equal_range_path(items: Sequence[Any], path: str, target: Any, reverse: bool=False, /) -> tuple[int, int]:
    """C++ equal_range over a path-sorted DDM batch.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_binary_search_path(items: Sequence[Any], path: str, target: Any, reverse: bool=False, /) -> int:
    """C++ binary search over a path-sorted DDM batch.

    Arguments are positional-only, matching the CPython method table.
    """
    ...

def batch_nth_path(items: Sequence[Any], path: str, n: int, largest: bool=False) -> Any:
    """C++ nth_element selection by DDM path.

    Accepts the named keyword parameters shown in the signature.
    """
    ...

def batch_mutate(items: Sequence[Any], operations: Sequence[Sequence[Any]], /) -> int:
    """Apply a compiled mutation plan across a DDM batch in one C++ pass.

    Arguments are positional-only, matching the CPython method table.
    """
    ...
