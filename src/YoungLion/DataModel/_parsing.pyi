"""Dependency-free compatibility helpers for dimensions and coordinate inputs."""
from collections.abc import Iterable, Sequence
from typing import Any

class ParseError(ValueError):
    """A conversion error carrying the original value and expected input shape."""
    message: str
    value: Any
    expected: str | None

    def __init__(self, message: str, value: Any=None, expected: str | None=None) -> None:
        """Store diagnostic context and include supplied context in the error text."""
        ...

def split_any(string: str, seps: Sequence[str]=('x', ',', ':', ';', '.')) -> list[str]:
    """Split on the first separator present, in seps order, and strip each part.

    Separators are literal strings, not regular expressions. Empty separators
    raise ValueError. If no separator matches, raise ParseError with context.
    """
    ...

def ensure_int_list(values: Iterable[Any], expected_len: int, name: str) -> list[int]:
    """Convert an iterable to exactly expected_len integers or raise ParseError.

    Uses Python int() conversion, including truncation of numeric floats.
    Conversion failures retain their cause and the original materialized values.
    The input is consumed once and never mutated.
    """
    ...

def enable_ansi() -> bool:
    """Enable Windows console ANSI mode when possible; report stdout color support.

    No terminal is changed on import. Redirected output returns False. This is
    an explicit compatibility helper; DDM display detects color on each call.
    """
    ...
