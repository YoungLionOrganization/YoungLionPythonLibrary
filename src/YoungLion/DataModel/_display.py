"""Bounded, cycle-aware DDM display without copying or serializing the model."""
from __future__ import annotations

from collections.abc import Mapping
from itertools import islice
import os
import reprlib
import sys
from typing import Any


def format_ddm(model: Any, *, indent: int, color: bool | None,
               max_depth: int, max_items: int, sort_keys: bool,
               include_private: bool) -> str:
    for name, value in (("indent", indent), ("max_depth", max_depth), ("max_items", max_items)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
    if max_depth > 100:
        raise ValueError("max_depth must be at most 100")
    if color is None:
        color = ("NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"
                 and bool(getattr(sys.stdout, "isatty", lambda: False)()))
    from ._core import DDM
    active: set[int] = set()
    scalar_repr = reprlib.Repr()
    scalar_repr.maxstring = 240
    scalar_repr.maxother = 240

    def paint(text: str, code: str) -> str:
        return f"\x1b[{code}m{text}\x1b[0m" if color else text

    def render(value: Any, depth: int) -> str:
        is_model = isinstance(value, DDM)
        mapping = value.__dict__ if is_model else value
        if is_model or isinstance(value, Mapping):
            opening, closing = (f"{type(value).__name__}({{", "})") if is_model else ("{", "}")
            entries = ((k, v) for k, v in mapping.items()
                       if not is_model or include_private or not isinstance(k, str) or not k.startswith("_"))
            if sort_keys:
                entries = iter(sorted(entries, key=lambda pair: (type(pair[0]).__name__, repr(pair[0]))))
            is_mapping = True
        elif isinstance(value, (list, tuple, set, frozenset)):
            opening, closing = ("[", "]") if isinstance(value, list) else ("(", ")")
            if isinstance(value, (set, frozenset)):
                opening, closing = ("{", "}") if isinstance(value, set) else ("frozenset({", "})")
                if not value:
                    return "set()" if isinstance(value, set) else "frozenset()"
            entries = iter(enumerate(value))
            is_mapping = False
        else:
            return paint(scalar_repr.repr(value), "32")
        if id(value) in active:
            return paint(f"<recursion: {type(value).__name__}>", "33")
        # Read one extra element to detect truncation without scanning/copying
        # a large unsorted container or mistaking a shared child for a cycle.
        selected = list(islice(entries, max_items + 1))
        if not selected:
            return opening + closing
        if depth >= max_depth:
            return opening + "..." + closing
        active.add(id(value))
        try:
            lines = []
            for key, child in selected[:max_items]:
                prefix = paint(scalar_repr.repr(key), "34") + ": " if is_mapping else ""
                lines.append(" " * (indent * (depth + 1)) + prefix + render(child, depth + 1) + ",")
            if len(selected) > max_items:
                lines.append(" " * (indent * (depth + 1)) + "... <more items>")
            return opening + "\n" + "\n".join(lines) + "\n" + " " * (indent * depth) + closing
        finally:
            active.remove(id(value))

    return render(model, 0)
