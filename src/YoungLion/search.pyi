"""YoungLion.search — ranked, fuzzy, autocomplete, structured and DDM-aware search.

This module provides a layered, dependency-free search toolkit.  Low-level native
similarity primitives feed reusable inverted/BM25 indexes; higher-level engines
cover autocomplete, multi-pattern matching, numeric ranges, structured records,
filesystem content and application search.  DDMSearchEngine adds reusable indexes
for dotted paths such as ``profile.name`` or ``economy.balance`` across ordinary
DDM-compatible iterables and YoungLion collection types.

The design separates one-time indexing cost from repeated query throughput.
Exact indexed lookups use hash structures; range operations use sorted index data;
ranked text search uses persistent posting lists/BM25; fuzzy matching is available
when exact terms are insufficient.  Mutating a source outside a collection-managed
path may require ``refresh()`` or ``invalidate()`` before querying again.

Compatibility classes GenerateTags, SearchData, Search and SearchFile remain
available for older call sites, while ApplicationSearch and DDMSearchEngine are
recommended for new application backends.
"""
from collections.abc import Hashable, Iterable, Iterator, Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Final

class SearchAlgorithm(str, Enum):
    """Search algorithm names.

    ``SearchAlgorithm`` provides stable symbolic constants/enum-like values used to choose matching strategies.

    When to use it
    --------------
    Use through SearchQuery/SearchIndex options rather than hard-coding implementation details.
    """
    AUTO = 'auto'
    HYBRID = 'hybrid'
    EXACT = 'exact'
    PREFIX = 'prefix'
    SUBSTRING = 'substring'
    REGEX = 'regex'
    LEVENSHTEIN = 'levenshtein'
    DAMERAU = 'damerau'
    JARO_WINKLER = 'jaro_winkler'
    TRIGRAM = 'trigram'
    BM25 = 'bm25'

class SearchDocument:
    """Indexed search document.

    ``SearchDocument`` provides document identity, source value, normalized text/tokens, tags, metadata and searchable-text composition.

    When to use it
    --------------
    Used internally and available for inspection/custom integrations.
    """
    id: Hashable
    text: str
    metadata: dict[str, Any]
    tags: tuple[str, ...]
    fields: dict[str, Any]

    def __init__(self, id: Hashable, text: str, metadata: dict[str, Any]=..., tags: tuple[str, ...]=(), fields: dict[str, Any]=...) -> None:
        ...

    def searchable_text(self) -> str:
        """Return the document fields combined into the text used for indexing/search."""
        ...

class SearchResult:
    """Ranked search result.

    ``SearchResult`` provides document reference, score and matching metadata with convenient source-value access.

    When to use it
    --------------
    Returned by result-oriented search APIs.
    """
    def __post_init__(self) -> None:
        """Initialize the internal ordering key from score after construction."""
        ...

    sort_index: float
    score: float
    document: SearchDocument
    algorithm: str
    positions: tuple[int, ...]
    matched_terms: tuple[str, ...]
    details: dict[str, float]

    def __init__(self, score: float, document: SearchDocument, algorithm: str='hybrid', positions: tuple[int, ...]=(), matched_terms: tuple[str, ...]=(), details: dict[str, float]=...) -> None:
        ...

    @property
    def value(self) -> Any:
        """Return the original application value associated with this search result."""
        ...

class SearchStats:
    """Search index statistics.

    ``SearchStats`` provides document/token/term counts describing an index snapshot.

    When to use it
    --------------
    Useful for diagnostics and monitoring.
    """
    documents: int
    tokens: int
    unique_tokens: int
    average_document_length: float

    def __init__(self, documents: int, tokens: int, unique_tokens: int, average_document_length: float) -> None:
        ...

class SearchQuery:
    """Normalized search request.

    ``SearchQuery`` provides query text plus algorithm, limits, scores, filters and regex flags.

    When to use it
    --------------
    Useful when constructing explicit repeatable search requests.
    """
    text: str
    algorithm: SearchAlgorithm | str
    limit: int | None
    min_score: float
    filters: Mapping[str, Any] | None
    regex_flags: int

    def __init__(self, text: str, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, limit: int | None=10, min_score: float=0.0, filters: Mapping[str, Any] | None=None, regex_flags: int=0) -> None:
        ...

class Posting:
    """Inverted-index posting.

    ``Posting`` provides document ID and term-frequency information.

    When to use it
    --------------
    Primarily useful for index inspection.
    """
    doc_id: Hashable
    term_frequency: int

    def __init__(self, doc_id: Hashable, term_frequency: int) -> None:
        ...

class AutocompleteEntry:
    """Autocomplete candidate.

    ``AutocompleteEntry`` provides display text, payload and ranking weight.

    When to use it
    --------------
    Stored by AutocompleteIndex.
    """
    term: str
    payload: Any
    weight: float

    def __init__(self, term: str, payload: Any=None, weight: float=1.0) -> None:
        ...

class PatternMatch:
    """Multi-pattern match record.

    ``PatternMatch`` provides matched pattern and text span metadata.

    When to use it
    --------------
    Returned by MultiPatternSearch.find.
    """
    pattern: str
    start: int
    end: int
    pattern_index: int

    def __init__(self, pattern: str, start: int, end: int, pattern_index: int) -> None:
        ...

class FuzzyMatcher:
    """Native-accelerated fuzzy string matcher.

    ``FuzzyMatcher`` provides Levenshtein, Damerau, Jaro-Winkler, trigram and hybrid similarity functions.

    When to use it
    --------------
    Use for typo-tolerant comparison; choose a metric appropriate to string length/error type.
    """

    @staticmethod
    def levenshtein(a: str, b: str, *, case_sensitive: bool=False) -> int:
        """Return native Levenshtein edit distance between two strings.

        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    @staticmethod
    def damerau_levenshtein(a: str, b: str, *, case_sensitive: bool=False) -> int:
        """Return native Damerau-Levenshtein distance including adjacent transpositions.

        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    @staticmethod
    def levenshtein_ratio(a: str, b: str, *, damerau: bool=False, case_sensitive: bool=False) -> float:
        """Return a normalized 0..1 similarity ratio derived from edit distance.

        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        damerau : bool (default: ``False``)
            Whether the normalized edit ratio uses Damerau-Levenshtein distance.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    @staticmethod
    def jaro_winkler(a: str, b: str, *, case_sensitive: bool=False) -> float:
        """Return Jaro-Winkler similarity, useful for short names and prefix-preserving typos.

        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    @staticmethod
    def trigram(a: str, b: str, *, case_sensitive: bool=False) -> float:
        """Return trigram Dice-style similarity between two strings.

        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    @staticmethod
    def hybrid(a: str, b: str, *, case_sensitive: bool=False) -> float:
        """Combine multiple fuzzy signals into a general-purpose normalized similarity score.

        Parameters
        ----------
        a : str
            First string/value.
        b : str
            Second string/value.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

class InvertedIndex:
    """Reusable token inverted index.

    ``InvertedIndex`` provides posting lists, prefix/fuzzy term expansion, candidates and BM25 scoring.

    When to use it
    --------------
    Usually accessed through SearchIndex; exposed for advanced index inspection.
    """

    def __init__(self) -> None:
        """Initialize a new InvertedIndex instance using the supplied configuration and input data.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def add(self, doc_id: Hashable, tokens: Iterable[str]) -> None:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        tokens : Iterable[str]
            Number of rate-limit tokens requested.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def remove(self, doc_id: Hashable) -> bool:
        """Remove an existing record/document/event and raise or report according to the class contract when absent.

        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def clear(self) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def tokens(self, doc_id: Hashable) -> tuple[str, ...]:
        """Perform the ``tokens`` operation for InvertedIndex.

        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def postings(self, term: str) -> tuple[Posting, ...]:
        """Perform the ``postings`` operation for InvertedIndex.

        Parameters
        ----------
        term : str
            Value supplied for ``term`` according to the InvertedIndex contract.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def terms(self) -> Iterator[str]:
        """Perform the ``terms`` operation for InvertedIndex.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def prefix_terms(self, prefix: str, *, limit: int | None=None) -> list[str]:
        """Return indexed terms beginning with a normalized prefix.

        Parameters
        ----------
        prefix : str
            Optional path/text prefix applied by the operation.
        limit : Optional[int] (default: ``None``)
            Maximum number of results/messages/suggestions to return.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def fuzzy_terms(self, query: str, *, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, threshold: float=0.6, limit: int=8) -> list[tuple[str, float]]:
        """Return similar indexed terms ranked by the selected fuzzy algorithm and threshold.

        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        algorithm : Union[SearchAlgorithm, str] (default: ``SearchAlgorithm.HYBRID``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        threshold : float (default: ``0.6``)
            Value supplied for ``threshold`` according to the InvertedIndex contract.
        limit : int (default: ``8``)
            Maximum number of results/messages/suggestions to return.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def candidate_ids(self, terms: Iterable[str]) -> set[Hashable]:
        """Return document IDs referenced by any of the supplied terms.

        Parameters
        ----------
        terms : Iterable[str]
            Search/index terms.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def bm25(self, query_tokens: Iterable[str], *, candidates: set[Hashable] | None=None, k1: float=1.5, b: float=0.75) -> dict[Hashable, float]:
        """Calculate BM25 relevance scores for query tokens over candidate documents.

        Parameters
        ----------
        query_tokens : Iterable[str]
            Value supplied for ``query_tokens`` according to the InvertedIndex contract.
        candidates : Optional[set[Hashable]] (default: ``None``)
            Value supplied for ``candidates`` according to the InvertedIndex contract.
        k1 : float (default: ``1.5``)
            BM25 term-frequency saturation parameter.
        b : float (default: ``0.75``)
            Second string/value.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    @property
    def document_count(self) -> int:
        """Return the number of documents currently represented by the index.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    @property
    def token_count(self) -> int:
        """Return the total number of indexed token occurrences.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    @property
    def unique_token_count(self) -> int:
        """Return the number of distinct indexed terms.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

class SearchIndex:
    """General-purpose ranked in-memory index.

    ``SearchIndex`` provides document lifecycle, filters and exact/contains/prefix/regex/fuzzy/BM25-oriented search.

    When to use it
    --------------
    Use for reusable text search where rebuilding per query would be wasteful.
    """

    def __init__(self, documents: Iterable[SearchDocument | Mapping[str, Any] | str] | None=None, *, case_sensitive: bool=False) -> None:
        """Initialize a new SearchIndex instance using the supplied configuration and input data.

        Parameters
        ----------
        documents : Optional[Iterable[Union[SearchDocument, Mapping[str, Any], str]]] (default: ``None``)
            Iterable of initial/additional documents.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def add(self, document: SearchDocument | Mapping[str, Any] | str, *, doc_id: Hashable | None=None) -> SearchDocument:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        document : Union[SearchDocument, Mapping[str, Any], str]
            Document/value to add to the index.
        doc_id : Optional[Hashable] (default: ``None``)
            Stable document identifier.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def extend(self, documents: Iterable[SearchDocument | Mapping[str, Any] | str]) -> SearchIndex:
        """Add several documents to the index.

        Parameters
        ----------
        documents : Iterable[Union[SearchDocument, Mapping[str, Any], str]]
            Iterable of initial/additional documents.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def remove(self, doc_id: Hashable) -> bool:
        """Remove an existing record/document/event and raise or report according to the class contract when absent.

        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def update(self, doc_id: Hashable, **changes: Any) -> SearchDocument:
        """Update top-level fields from mapping arguments and keyword values.

        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        **changes : Any
            Value supplied for ``changes`` according to the SearchIndex contract.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def clear(self) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[SearchDocument]:
        ...

    def stats(self) -> SearchStats:
        """Return diagnostic counts describing the current cache/index/processor state.

        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    @property
    def inverted_index(self) -> InvertedIndex:
        """Expose the reusable InvertedIndex backing this SearchIndex.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def search(self, query: str | SearchQuery, *, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, limit: int | None=10, min_score: float=0.0, filters: Mapping[str, Any] | None=None, regex_flags: int=0) -> list[SearchResult]:
        """Search the current data/index using the query and options supported by this class.

        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        algorithm : Union[SearchAlgorithm, str] (default: ``SearchAlgorithm.HYBRID``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        limit : Optional[int] (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        min_score : float (default: ``0.0``)
            Minimum normalized/relevance score required for returned results.
        filters : Optional[Mapping[str, Any]] (default: ``None``)
            Optional field/metadata filters applied to candidate documents.
        regex_flags : int (default: ``0``)
            Flags passed to regular-expression matching.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

class BM25Index(SearchIndex):
    """BM25-focused SearchIndex.

    ``BM25Index`` provides SearchIndex behavior with BM25 as the natural ranked retrieval path.

    When to use it
    --------------
    Use for document relevance ranking over repeated queries.
    """

    def search(self, query: str | SearchQuery, **kwargs: Any) -> list[SearchResult]:
        """Search the current data/index using the query and options supported by this class.

        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        ...

class AutocompleteIndex:
    """Weighted autocomplete index.

    ``AutocompleteIndex`` provides prefix suggestions with optional fuzzy fallback and payloads.

    When to use it
    --------------
    Use for command palettes, search boxes and route/entity completion.
    """

    def __init__(self, entries: Iterable[str | AutocompleteEntry | tuple[str, Any] | tuple[str, Any, float]]=(), *, case_sensitive: bool=False) -> None:
        """Initialize a new AutocompleteIndex instance using the supplied configuration and input data.

        Parameters
        ----------
        entries : Iterable[Union[str, AutocompleteEntry, Tuple[str, Any], Tuple[str, Any, float]]] (default: ``()``)
            Initial autocomplete/index entries.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    def add(self, entry: str | AutocompleteEntry | tuple[str, Any] | tuple[str, Any, float], payload: Any=None, weight: float=1.0) -> AutocompleteEntry:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        entry : Union[str, AutocompleteEntry, Tuple[str, Any], Tuple[str, Any, float]]
            Structured or textual log entry to persist.
        payload : Any (default: ``None``)
            Application value associated with an indexed entry/document.
        weight : float (default: ``1.0``)
            Ranking weight applied to an autocomplete entry.
        """
        ...

    def suggest(self, prefix: str, *, limit: int=10, fuzzy_fallback: bool=True, min_score: float=0.62) -> list[AutocompleteEntry]:
        """Return ranked autocomplete candidates for a prefix with optional fuzzy fallback.

        Parameters
        ----------
        prefix : str
            Optional path/text prefix applied by the operation.
        limit : int (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        fuzzy_fallback : bool (default: ``True``)
            Whether autocomplete may fall back to fuzzy matching when prefix matches are insufficient.
        min_score : float (default: ``0.62``)
            Minimum normalized/relevance score required for returned results.
        """
        ...

    def __len__(self) -> int:
        ...

class MultiPatternSearch:
    """Aho-Corasick style multi-pattern matcher.

    ``MultiPatternSearch`` provides one-pass discovery of many literal patterns in text.

    When to use it
    --------------
    Use for moderation keywords, signatures and dictionary matching.
    """

    def __init__(self, patterns: Iterable[str], *, case_sensitive: bool=False) -> None:
        """Initialize a new MultiPatternSearch instance using the supplied configuration and input data.

        Parameters
        ----------
        patterns : Iterable[str]
            Patterns indexed by MultiPatternSearch.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    def find(self, text: str) -> list[PatternMatch]:
        """Return tree/search records that satisfy a predicate or query.

        Parameters
        ----------
        text : str
            Text/content input.
        """
        ...

    def contains_any(self, text: str) -> bool:
        """Return whether any configured pattern occurs in the supplied text.

        Parameters
        ----------
        text : str
            Text/content input.
        """
        ...

class NumericSearch:
    """Sorted numeric search index.

    ``NumericSearch`` provides range lookup and nearest-neighbor queries over numeric values with payloads.

    When to use it
    --------------
    Use for prices, scores, measurements and other one-dimensional numeric fields.
    """

    def __init__(self, values: Iterable[tuple[float, Any]]=()) -> None:
        """Initialize a new NumericSearch instance using the supplied configuration and input data.

        Parameters
        ----------
        values : Iterable[Tuple[float, Any]] (default: ``()``)
            Input iterable, mapping values or composite lookup values.
        """
        ...

    def add(self, value: float, payload: Any=None) -> None:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        value : float
            Target, new or comparison value.
        payload : Any (default: ``None``)
            Application value associated with an indexed entry/document.
        """
        ...

    def range(self, minimum: float, maximum: float) -> list[tuple[float, Any]]:
        """Return indexed entries inside numeric/string bounds according to inclusion flags.

        Parameters
        ----------
        minimum : float
            Lower bound or minimum accepted value.
        maximum : float
            Upper bound or maximum accepted value.
        """
        ...

    def nearest(self, value: float, k: int=1) -> list[tuple[float, Any]]:
        """Return the k numerically nearest indexed entries to a target value.

        Parameters
        ----------
        value : float
            Target, new or comparison value.
        k : int (default: ``1``)
            Value supplied for ``k`` according to the NumericSearch contract.
        """
        ...

    def __len__(self) -> int:
        ...

class StructuredSearch:
    """Field-weighted record search.

    ``StructuredSearch`` provides indexing mapping-like records with configurable field weights.

    When to use it
    --------------
    Use when free-text relevance must span several known structured fields.
    """

    def __init__(self, records: Iterable[Mapping[str, Any]]=(), *, id_field: str='id', field_weights: Mapping[str, float] | None=None, case_sensitive: bool=False) -> None:
        """Initialize a new StructuredSearch instance using the supplied configuration and input data.

        Parameters
        ----------
        records : Iterable[Mapping[str, Any]] (default: ``()``)
            Input records for structured/DDM collection indexing.
        id_field : str (default: ``'id'``)
            Record field used to derive stable document identifiers.
        field_weights : Optional[Mapping[str, float]] (default: ``None``)
            Per-field search ranking weights.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    def add(self, record: Mapping[str, Any]) -> SearchDocument:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        record : Mapping[str, Any]
            Value supplied for ``record`` according to the StructuredSearch contract.
        """
        ...

    def search(self, query: str | SearchQuery, **kwargs: Any) -> list[SearchResult]:
        """Search the current data/index using the query and options supported by this class.

        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        ...

class FileSearchEngine:
    """Filesystem search backend.

    ``FileSearchEngine`` provides path/name metadata indexing with optional bounded file-content indexing.

    When to use it
    --------------
    Use for local application file search; call refresh after external filesystem changes.
    """

    def __init__(self, root: str | Path='.', *, content: bool=False, max_content_bytes: int=2000000, extensions: Iterable[str] | None=None, case_sensitive: bool=False) -> None:
        """Initialize a new FileSearchEngine instance using the supplied configuration and input data.

        Parameters
        ----------
        root : Union[str, Path] (default: ``'.'``)
            Root directory for filesystem search.
        content : bool (default: ``False``)
            Text/bytes/content payload to write, search or convert.
        max_content_bytes : int (default: ``2000000``)
            Value supplied for ``max_content_bytes`` according to the FileSearchEngine contract.
        extensions : Optional[Iterable[str]] (default: ``None``)
            Allowed file extensions, typically including leading dots.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    def refresh(self) -> FileSearchEngine:
        """Rebuild class-specific cached/indexed state from the current source."""
        ...

    def search_results(self, query: str | SearchQuery, *, extension: str | Sequence[str] | None=None, min_size: int | None=None, max_size: int | None=None, **kwargs: Any) -> list[SearchResult]:
        """Return rich SearchResult-style objects rather than only application payloads/values.

        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        extension : Optional[Union[str, Sequence[str]]] (default: ``None``)
            Value supplied for ``extension`` according to the FileSearchEngine contract.
        min_size : Optional[int] (default: ``None``)
            Optional minimum file/content size filter.
        max_size : Optional[int] (default: ``None``)
            Maximum number of cache entries retained.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        ...

    def search(self, query: str | SearchQuery, **kwargs: Any) -> list[str]:
        """Search the current data/index using the query and options supported by this class.

        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        ...

class GenerateTags:
    """Legacy tag generator.

    ``GenerateTags`` provides normalization, replacement, stop-word filtering and n-gram style tag generation.

    When to use it
    --------------
    Retained for compatibility; new full-text systems should prefer SearchIndex/ApplicationSearch.
    """

    def __init__(self, terms: str | list[str], lowercase: bool=True, clean_special_chars: bool=True, min_words: int=1, max_words: int | None=None, replacements: dict[str, str] | None=None, stop_words: list[str] | None=None, max_tags: int=10000) -> None:
        """Initialize a new GenerateTags instance using the supplied configuration and input data.

        Parameters
        ----------
        terms : Union[str, List[str]]
            Search/index terms.
        lowercase : bool (default: ``True``)
            Value supplied for ``lowercase`` according to the GenerateTags contract.
        clean_special_chars : bool (default: ``True``)
            Value supplied for ``clean_special_chars`` according to the GenerateTags contract.
        min_words : int (default: ``1``)
            Minimum words per generated tag.
        max_words : Optional[int] (default: ``None``)
            Maximum words per generated tag.
        replacements : Optional[dict] (default: ``None``)
            Text replacement mapping used while generating tags.
        stop_words : Optional[List[str]] (default: ``None``)
            Words excluded from generated tags.
        max_tags : int (default: ``10000``)
            Maximum generated tags retained.
        """
        ...

    def get_tags(self) -> list[str]:
        """Return normalized/generated tags for the legacy compatibility object."""
        ...

class SearchData:
    """Legacy tag-to-data adapter.

    ``SearchData`` provides tag generation and retrieval over a collection of values.

    When to use it
    --------------
    Retained for compatibility.
    """

    def __init__(self, data: list[dict[str, Any]]) -> None:
        """Initialize a new SearchData instance using the supplied configuration and input data.

        Parameters
        ----------
        data : List[Dict[str, Any]]
            Input mapping or record data used to initialize the object.
        """
        ...

    def get_tags(self) -> list[str]:
        """Return normalized/generated tags for the legacy compatibility object."""
        ...

    def get(self, tag: str) -> list[Any]:
        """Return a value for a key, falling back to a default when the key is absent.

        Parameters
        ----------
        tag : str
            Value supplied for ``tag`` according to the SearchData contract.
        """
        ...

    def __getitem__(self, tag: str) -> list[Any]:
        ...

    def __contains__(self, tag: object) -> bool:
        ...

    def __repr__(self) -> str:
        ...

class Search:
    """Legacy compatibility search facade.

    ``Search`` provides simple query and ranked query methods over SearchData.

    When to use it
    --------------
    Use ApplicationSearch/SearchIndex for new systems.
    """

    def __init__(self, sdata: SearchData, only_tag: bool=False) -> None:
        """Initialize a new Search instance using the supplied configuration and input data.

        Parameters
        ----------
        sdata : SearchData
            SearchData instance used by the compatibility Search facade.
        only_tag : bool (default: ``False``)
            Restrict compatibility search behavior to tags where supported.
        """
        ...

    def search(self, query: str) -> list[Any]:
        """Search the current data/index using the query and options supported by this class.

        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        """
        ...

    def ranked(self, query: str, **kwargs: Any) -> list[SearchResult]:
        """Run the legacy facade through the ranked search engine and return scored results.

        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        ...

class SearchFile:
    """Legacy filesystem search facade.

    ``SearchFile`` provides simple name/content search rooted at a directory.

    When to use it
    --------------
    Use FileSearchEngine for richer result metadata and indexing.
    """

    def __init__(self, root: str | Path='.') -> None:
        """Initialize a new SearchFile instance using the supplied configuration and input data.

        Parameters
        ----------
        root : Union[str, Path] (default: ``'.'``)
            Root directory for filesystem search.
        """
        ...

    def search(self, query: str, content: bool=False, case_sensitive: bool=False) -> list[str]:
        """Search the current data/index using the query and options supported by this class.

        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        content : bool (default: ``False``)
            Text/bytes/content payload to write, search or convert.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

class DDMSearchHit:
    """DDM text-search hit.

    ``DDMSearchHit`` provides source key/object, path value and score metadata.

    When to use it
    --------------
    Returned when DDMSearchEngine.text is requested with hit metadata.
    """
    item: Any
    key: Any
    path: str
    value: Any
    score: float
    algorithm: str

    def __init__(self, item: Any, key: Any, path: str, value: Any, score: float=1.0, algorithm: str='exact') -> None:
        ...

class DDMPathIndex:
    """Single dotted-path DDM index.

    ``DDMPathIndex`` provides exact hash lookup, sorted ranges, prefix/contains and optional text index.

    When to use it
    --------------
    Built by DDMSearchEngine and reusable across many queries.
    """
    path: str
    case_sensitive: bool

    def __init__(self, path: str, entries: Sequence[tuple[Any, Any]], *, text: bool=True, case_sensitive: bool=False, objects: Mapping[Any, Any] | None=None) -> None:
        """Initialize a new DDMPathIndex instance using the supplied configuration and input data.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        entries : Sequence[Tuple[Any, Any]]
            Initial autocomplete/index entries.
        text : bool (default: ``True``)
            Text/content input.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        objects : Optional[Mapping[Any, Any]] (default: ``None``)
            Optional shared key-to-object mapping reused by DDM indexes.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def exact(self, value: Any) -> list[DDMSearchHit]:
        """Return records whose indexed dotted-path value exactly equals the target.

        Parameters
        ----------
        value : Any
            Target, new or comparison value.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def range(self, minimum: Any=None, maximum: Any=None, *, include_min: bool=True, include_max: bool=True) -> list[DDMSearchHit]:
        """Return indexed entries inside numeric/string bounds according to inclusion flags.

        Parameters
        ----------
        minimum : Any (default: ``None``)
            Lower bound or minimum accepted value.
        maximum : Any (default: ``None``)
            Upper bound or maximum accepted value.
        include_min : bool (default: ``True``)
            Whether a lower range bound is inclusive.
        include_max : bool (default: ``True``)
            Whether an upper range bound is inclusive.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def prefix(self, prefix: str, *, limit: int | None=None) -> list[DDMSearchHit]:
        """Return records whose indexed string value begins with the supplied prefix.

        Parameters
        ----------
        prefix : str
            Optional path/text prefix applied by the operation.
        limit : Optional[int] (default: ``None``)
            Maximum number of results/messages/suggestions to return.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def text(self, query: str, *, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, limit: int | None=10, min_score: float=0.0) -> list[DDMSearchHit]:
        """Perform the ``text`` operation for DDMPathIndex.

        Parameters
        ----------
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        algorithm : Union[SearchAlgorithm, str] (default: ``SearchAlgorithm.HYBRID``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        limit : Optional[int] (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        min_score : float (default: ``0.0``)
            Minimum normalized/relevance score required for returned results.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def contains(self, needle: Any, *, case_sensitive: bool | None=None) -> list[DDMSearchHit]:
        """Return whether a value/substring lies within the represented range or indexed path data.

        Parameters
        ----------
        needle : Any
            Value supplied for ``needle`` according to the DDMPathIndex contract.
        case_sensitive : Optional[bool] (default: ``None``)
            Whether string matching preserves case instead of using case-folded comparison.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def stats(self) -> dict[str, int]:
        """Return diagnostic counts describing the current cache/index/processor state.

        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

class DDMCompositeIndex:
    """Composite exact DDM index.

    ``DDMCompositeIndex`` provides hash lookup over a tuple of multiple dotted-path values.

    When to use it
    --------------
    Use for repeated equality queries that constrain the same field combination.
    """

    def __init__(self, paths: Sequence[str], entries: Sequence[tuple[Any, Any]], *, objects: Mapping[Any, Any] | None=None) -> None:
        """Initialize a new DDMCompositeIndex instance using the supplied configuration and input data.

        Parameters
        ----------
        paths : Sequence[str]
            Dotted paths participating in an index/composite operation.
        entries : Sequence[Tuple[Any, Any]]
            Initial autocomplete/index entries.
        objects : Optional[Mapping[Any, Any]] (default: ``None``)
            Optional shared key-to-object mapping reused by DDM indexes.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def find(self, *values: Any) -> list[Any]:
        """Return tree/search records that satisfy a predicate or query.

        Parameters
        ----------
        *values : Any
            Input iterable, mapping values or composite lookup values.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

class DDMSearchEngine:
    """Nested structured-data search engine.

    ``DDMSearchEngine`` provides shared record snapshot plus reusable exact/range/text/composite dotted-path indexes and scan fallback.

    When to use it
    --------------
    Use for large DDM-compatible datasets and queries such as profile.name or economy.balance.

    Index strategy
    --------------
    The engine shares one source/object snapshot across path/composite indexes to avoid repeating the same object map for every indexed field. Exact indexes use hash maps, range-friendly values use sorted data, and optional text indexes use YoungLion SearchIndex.

    Example::

        engine = DDMSearchEngine(users).create_indexes(
            "id", "profile.name", "profile.age"
        )
        alice = engine.find_one("profile.name", "Alice")
        adults = engine.between("profile.age", 18, 65)
    """

    def __init__(self, source: Any, *, case_sensitive: bool=False) -> None:
        """Initialize a new DDMSearchEngine instance using the supplied configuration and input data.

        Parameters
        ----------
        source : Any
            Source path, collection or transfer identifier.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def refresh(self) -> DDMSearchEngine:
        """Rebuild class-specific cached/indexed state from the current source.


        Notes
        -----
        Refresh rebuilds the source snapshot and cached indexes. Use it after structural/external source mutations that the engine could not observe automatically.
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def invalidate(self, paths: Iterable[str] | None=None) -> None:
        """Invalidate cached lazy fields so they will be recomputed on next access.

        Parameters
        ----------
        paths : Optional[Iterable[str]] (default: ``None``)
            Dotted paths participating in an index/composite operation.


        Notes
        -----
        Path-only invalidation allows targeted indexes to be rebuilt while retaining the shared record snapshot when source structure itself has not changed.
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def create_index(self, path: str, *, text: bool=True) -> DDMPathIndex:
        """Create and cache an index for one dotted path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        text : bool (default: ``True``)
            Text/content input.


        Notes
        -----
        Index construction has an upfront time/memory cost but can turn repeated exact queries into hash lookups and repeated ranges into sorted-index operations.
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def create_indexes(self, *paths: str, text: bool=True) -> DDMSearchEngine:
        """Create indexes for several dotted paths and return the engine for fluent setup.

        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        text : bool (default: ``True``)
            Text/content input.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def create_composite_index(self, *paths: str) -> DDMCompositeIndex:
        """Create a reusable exact index over a tuple of dotted paths.

        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def find(self, path: str, value: Any=None, *, op: str='eq', limit: int | None=None, use_index: bool=True) -> list[Any]:
        """Return tree/search records that satisfy a predicate or query.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        limit : Optional[int] (default: ``None``)
            Maximum number of results/messages/suggestions to return.
        use_index : bool (default: ``True``)
            Value supplied for ``use_index`` according to the DDMSearchEngine contract.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def find_one(self, path: str, value: Any=None, *, op: str='eq', default: Any=None, use_index: bool=True) -> Any:
        """Return the first matching record for a dotted-path comparison or a default.

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
        use_index : bool (default: ``True``)
            Value supplied for ``use_index`` according to the DDMSearchEngine contract.

        Returns
        -------
        First matching source record, or the caller-provided default.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def exists(self, path: str, value: Any=None, *, op: str='eq') -> bool:
        """Return whether any record satisfies the dotted-path comparison.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.

        Returns
        -------
        ``True`` if at least one matching record exists.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def count(self, path: str, value: Any=None, *, op: str='eq') -> int:
        """Return the number of stored values or matching records, depending on the class.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.

        Returns
        -------
        Number of records/fields matching the method semantics.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def between(self, path: str, minimum: Any, maximum: Any, *, include_min: bool=True, include_max: bool=True) -> list[Any]:
        """Return records whose dotted-path value falls within the requested bounds.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        minimum : Any
            Lower bound or minimum accepted value.
        maximum : Any
            Upper bound or maximum accepted value.
        include_min : bool (default: ``True``)
            Whether a lower range bound is inclusive.
        include_max : bool (default: ``True``)
            Whether an upper range bound is inclusive.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def text(self, path: str, query: str, *, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, limit: int | None=10, min_score: float=0.0, hits: bool=False) -> Any:
        """Perform the ``text`` operation for DDMSearchEngine.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        algorithm : Union[SearchAlgorithm, str] (default: ``SearchAlgorithm.HYBRID``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        limit : Optional[int] (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        min_score : float (default: ``0.0``)
            Minimum normalized/relevance score required for returned results.
        hits : bool (default: ``False``)
            Whether DDM text search returns DDMSearchHit metadata instead of only source objects.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def composite(self, paths: Sequence[str], values: Sequence[Any]) -> list[Any]:
        """Query a previously built composite dotted-path index.

        Parameters
        ----------
        paths : Sequence[str]
            Dotted paths participating in an index/composite operation.
        values : Sequence[Any]
            Input iterable, mapping values or composite lookup values.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def where(self, **lookups: Any) -> list[Any]:
        """Apply one or more structured lookup expressions and return matching records.

        Parameters
        ----------
        **lookups : Any
            Structured lookup expressions supplied as keyword arguments.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.

        Example::

            active_adults = engine.where(
                active__eq=True,
                profile__age__gte=18,
            )
        """
        ...

    def order_by(self, path: str, *, reverse: bool=False, missing_last: bool=True) -> list[Any]:
        """Return source records ordered by a dotted-path value.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        missing_last : bool (default: ``True``)
            Whether records lacking the sort path should be placed after records with values.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def values(self, path: str, default: Any=None) -> list[Any]:
        """Return a dynamic view or collection of stored values.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def stats(self) -> dict[str, Any]:
        """Return diagnostic counts describing the current cache/index/processor state.

        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...
    index = create_index
    query = where

class ApplicationSearch:
    """Application-facing search backend.

    ``ApplicationSearch`` provides document CRUD, ranked results, payload retrieval, autocomplete, facets and statistics.

    When to use it
    --------------
    Use for command palettes, help centers, settings, product/catalog and local app search.
    """

    def __init__(self, *, case_sensitive: bool=False) -> None:
        """Initialize a new ApplicationSearch instance using the supplied configuration and input data.

        Parameters
        ----------
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def add(self, doc_id: Hashable, title: str, body: str='', *, tags: Iterable[str]=(), fields: Mapping[str, Any] | None=None, payload: Any=None, autocomplete_weight: float=1.0) -> SearchDocument:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        title : str
            Value supplied for ``title`` according to the ApplicationSearch contract.
        body : str (default: ``''``)
            Plain-text message body.
        tags : Iterable[str] (default: ``()``)
            Value supplied for ``tags`` according to the ApplicationSearch contract.
        fields : Optional[Mapping[str, Any]] (default: ``None``)
            Field names or field mapping used for structured document data.
        payload : Any (default: ``None``)
            Application value associated with an indexed entry/document.
        autocomplete_weight : float (default: ``1.0``)
            Weight assigned to the document title in autocomplete ranking.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.

        Example::

            search.add(
                "cmd.settings", "Settings", "Open application settings",
                tags=["config"], fields={"category": "system"},
                payload={"route": "/settings"},
            )
        """
        ...

    def update(self, doc_id: Hashable, *, title: str | None=None, body: str | None=None, tags: Iterable[str] | None=None, fields: Mapping[str, Any] | None=None, payload: Any=..., autocomplete_weight: float | None=None) -> SearchDocument:
        """Update top-level fields from mapping arguments and keyword values.

        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.
        title : Optional[str] (default: ``None``)
            Value supplied for ``title`` according to the ApplicationSearch contract.
        body : Optional[str] (default: ``None``)
            Plain-text message body.
        tags : Optional[Iterable[str]] (default: ``None``)
            Value supplied for ``tags`` according to the ApplicationSearch contract.
        fields : Optional[Mapping[str, Any]] (default: ``None``)
            Field names or field mapping used for structured document data.
        payload : Any (default: ``_SEARCH_MISSING``)
            Application value associated with an indexed entry/document.
        autocomplete_weight : Optional[float] (default: ``None``)
            Weight assigned to the document title in autocomplete ranking.


        Notes
        -----
        Updates rebuild the affected indexed/autocomplete state so stale title/body suggestions are not retained.
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def remove(self, doc_id: Hashable) -> bool:
        """Remove an existing record/document/event and raise or report according to the class contract when absent.

        Parameters
        ----------
        doc_id : Hashable
            Stable document identifier.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def search_results(self, query: str | SearchQuery, **kwargs: Any) -> list[SearchResult]:
        """Return rich SearchResult-style objects rather than only application payloads/values.

        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def search(self, query: str | SearchQuery, **kwargs: Any) -> list[Any]:
        """Search the current data/index using the query and options supported by this class.

        Parameters
        ----------
        query : Union[str, SearchQuery]
            Search text, structured query or SQL/XML expression according to the method.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def suggest(self, prefix: str, *, limit: int=10, fuzzy: bool=True) -> list[AutocompleteEntry]:
        """Return ranked autocomplete candidates for a prefix with optional fuzzy fallback.

        Parameters
        ----------
        prefix : str
            Optional path/text prefix applied by the operation.
        limit : int (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        fuzzy : bool (default: ``True``)
            Whether suggestions may use fuzzy fallback.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def facet(self, field: str, *, query: str | None=None, limit: int | None=None) -> list[tuple[Any, int]]:
        """Count values for one field, optionally restricted to documents matching a query.

        Parameters
        ----------
        field : str
            Field name used for a facet or structured operation.
        query : Optional[str] (default: ``None``)
            Search text, structured query or SQL/XML expression according to the method.
        limit : Optional[int] (default: ``None``)
            Maximum number of results/messages/suggestions to return.


        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...

    def stats(self) -> SearchStats:
        """Return diagnostic counts describing the current cache/index/processor state.

        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.

        Notes
        -----
        Indexes are in-memory and process-local. Reuse the same index/engine for repeated queries to amortize index construction cost.
        """
        ...
SearchEngine = ApplicationSearch
DDMIndex = DDMPathIndex

def tokenize(text: Any, *, case_sensitive: bool=False, min_length: int=1) -> list[str]:
    """Normalize text into the token sequence used by YoungLion search indexes.

    Parameters
    ----------
    text : Any
        Text/content input.
    case_sensitive : bool (default: ``False``)
        Whether string matching preserves case instead of using case-folded comparison.
    min_length : int (default: ``1``)
        Minimum token length retained by tokenization.
    """
    ...
