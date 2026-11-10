"""Dependency-free compatibility helpers for dimensions and coordinate inputs."""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any


class ParseError(ValueError):
    """A conversion error carrying the original value and expected input shape."""

    def __init__(self, message: str, value: Any = None, expected: str | None = None) -> None:
        """Store diagnostic context and include supplied context in the error text."""
        self.message = message
        self.value = value
        self.expected = expected
        text = message
        if value is not None:
            text += f"\n  Got value: {value!r}"
        if expected is not None:
            text += f"\n  Expected: {expected}"
        super().__init__(text)


def split_any(string: str, seps: Sequence[str] = ("x", ",", ":", ";", ".")) -> list[str]:
    """Split on the first separator present, in seps order, and strip each part.

    Separators are literal strings, not regular expressions. Empty separators
    raise ValueError. If no separator matches, raise ParseError with context.
    """
    for sep in seps:
        if not sep:
            raise ValueError("separators must not be empty")
        if sep in string:
            return [part.strip() for part in string.split(sep)]
    raise ParseError("Could not detect a valid separator", string, f"one of {tuple(seps)!r}")


def ensure_int_list(values: Iterable[Any], expected_len: int, name: str) -> list[int]:
    """Convert an iterable to exactly expected_len integers or raise ParseError.

    Uses Python int() conversion, including truncation of numeric floats.
    Conversion failures retain their cause and the original materialized values.
    The input is consumed once and never mutated.
    """
    data = list(values)
    if len(data) != expected_len:
        raise ParseError(f"{name} has incorrect number of values", data, f"exactly {expected_len} values")
    try:
        return [int(value.strip() if isinstance(value, str) else value) for value in data]
    except (ValueError, TypeError, OverflowError) as exc:
        raise ParseError(f"{name} values cannot be converted to integers", data, "integer-compatible values") from exc


def enable_ansi() -> bool:
    """Enable Windows console ANSI mode when possible; report stdout color support.

    No terminal is changed on import. Redirected output returns False. This is
    an explicit compatibility helper; DDM display detects color on each call.
    """
    import os
    import sys
    if not getattr(sys.stdout, "isatty", lambda: False)() or "NO_COLOR" in os.environ:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.windll.kernel32
        kernel.GetStdHandle.restype = wintypes.HANDLE
        kernel.GetStdHandle.argtypes = [wintypes.DWORD]
        kernel.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        handle = kernel.GetStdHandle(-11)
        mode = wintypes.DWORD()
        return bool(kernel.GetConsoleMode(handle, ctypes.byref(mode))
                    and kernel.SetConsoleMode(handle, mode.value | 4))
    return os.environ.get("TERM") != "dumb"
