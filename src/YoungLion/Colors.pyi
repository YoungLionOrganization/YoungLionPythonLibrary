"""YoungLion.Colors — dependency-free ANSI terminal color and styling utilities.

This module provides the :class:`Colors` namespace used throughout YoungLion for
portable terminal presentation.  It exposes the traditional ANSI style constants
expected by small scripts while also supporting true-color RGB sequences,
ANSI-256 foreground/background colors, safe stripping, style composition and
text gradients.

The API is deliberately dependency-free.  It does not install terminal drivers,
change global output streams, or require a rendering framework.  Callers decide
whether to emit the returned escape sequences and can use :meth:`Colors.strip`
when plain text is required for logs, files, tests, or non-ANSI terminals.

Typical uses
------------
* Add readable severity or status coloring to command-line applications.
* Generate 24-bit foreground/background colors from application theme values.
* Remove ANSI control sequences before persisting console output.
* Build compact gradients or combine multiple ANSI styles without dependencies.

Example
-------
    from YoungLion import Colors

    label = Colors.wrap("READY", Colors.BRIGHT_GREEN, Colors.BOLD)
    print(label)
    assert Colors.strip(label) == "READY"

Notes
-----
All helpers return strings and do not print by themselves.  Terminal capability
checking belongs to the caller or to :class:`YoungLion.Terminal` when automatic
presentation decisions are required.
"""
from typing import ClassVar

class Colors:
    """ANSI styling namespace.

    ``Colors`` provides classic ANSI constants, true-color, ANSI-256, stripping, wrapping and gradients.

    When to use it
    --------------
    Use to construct style sequences; pair with Terminal.supports_color when capability detection is required.
    """
    RESET: ClassVar[str]
    BRIGHT: ClassVar[str]
    DIM: ClassVar[str]
    ITALIC: ClassVar[str]
    UNDERLINE: ClassVar[str]
    BLINK: ClassVar[str]
    REVERSE: ClassVar[str]
    HIDDEN: ClassVar[str]
    STRIKETHROUGH: ClassVar[str]
    BLACK: ClassVar[str]
    RED: ClassVar[str]
    GREEN: ClassVar[str]
    YELLOW: ClassVar[str]
    BLUE: ClassVar[str]
    MAGENTA: ClassVar[str]
    CYAN: ClassVar[str]
    WHITE: ClassVar[str]
    BRIGHT_BLACK: ClassVar[str]
    BRIGHT_RED: ClassVar[str]
    BRIGHT_GREEN: ClassVar[str]
    BRIGHT_YELLOW: ClassVar[str]
    BRIGHT_BLUE: ClassVar[str]
    BRIGHT_MAGENTA: ClassVar[str]
    BRIGHT_CYAN: ClassVar[str]
    BRIGHT_WHITE: ClassVar[str]
    BG_BLACK: ClassVar[str]
    BG_RED: ClassVar[str]
    BG_GREEN: ClassVar[str]
    BG_YELLOW: ClassVar[str]
    BG_BLUE: ClassVar[str]
    BG_MAGENTA: ClassVar[str]
    BG_CYAN: ClassVar[str]
    BG_WHITE: ClassVar[str]
    BG_BRIGHT_BLACK: ClassVar[str]
    BG_BRIGHT_RED: ClassVar[str]
    BG_BRIGHT_GREEN: ClassVar[str]
    BG_BRIGHT_YELLOW: ClassVar[str]
    BG_BRIGHT_BLUE: ClassVar[str]
    BG_BRIGHT_MAGENTA: ClassVar[str]
    BG_BRIGHT_CYAN: ClassVar[str]
    BG_BRIGHT_WHITE: ClassVar[str]

    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> str:
        """Return an ANSI true-color foreground escape sequence for the supplied RGB channels.

        Parameters
        ----------
        r : int
            Red channel 0..255.
        g : int
            Green channel 0..255.
        b : int
            Second string/value.
        """
        ...

    @classmethod
    def bg_rgb(cls, r: int, g: int, b: int) -> str:
        """Return an ANSI true-color background escape sequence for the supplied RGB channels.

        Parameters
        ----------
        r : int
            Red channel 0..255.
        g : int
            Green channel 0..255.
        b : int
            Second string/value.
        """
        ...

    @staticmethod
    def ansi256(index: int) -> str:
        """Return an ANSI-256 foreground escape sequence.

        Parameters
        ----------
        index : int
            Value supplied for ``index`` according to the Colors contract.
        """
        ...

    @staticmethod
    def bg_ansi256(index: int) -> str:
        """Return an ANSI-256 background escape sequence.

        Parameters
        ----------
        index : int
            Value supplied for ``index`` according to the Colors contract.
        """
        ...

    @staticmethod
    def strip(text: object) -> str:
        """Remove ANSI control sequences from text.

        Parameters
        ----------
        text : object
            Text/content input.
        """
        ...

    @classmethod
    def wrap(cls, text: object, *styles: str, reset: bool=True) -> str:
        """Wrap text in one or more ANSI style sequences and optionally append reset.

        Parameters
        ----------
        text : object
            Text/content input.
        *styles : str
            Value supplied for ``styles`` according to the Colors contract.
        reset : bool (default: ``True``)
            Value supplied for ``reset`` according to the Colors contract.
        """
        ...

    @classmethod
    def foreground(cls, rgb: tuple[int, int, int], text: object) -> str:
        """Apply an RGB foreground color to text.

        Parameters
        ----------
        rgb : Tuple[int, int, int]
            Value supplied for ``rgb`` according to the Colors contract.
        text : object
            Text/content input.
        """
        ...

    @classmethod
    def background(cls, rgb: tuple[int, int, int], text: object) -> str:
        """Apply an RGB background color to text.

        Parameters
        ----------
        rgb : Tuple[int, int, int]
            Value supplied for ``rgb`` according to the Colors contract.
        text : object
            Text/content input.
        """
        ...

    @classmethod
    def gradient(cls, text: str, start: tuple[int, int, int], end: tuple[int, int, int]) -> str:
        """Apply a linear RGB foreground gradient across the characters of a string.

        Parameters
        ----------
        text : str
            Text/content input.
        start : Tuple[int, int, int]
            Whether the stopwatch starts immediately or remains stopped initially.
        end : Tuple[int, int, int]
            Value supplied for ``end`` according to the Colors contract.
        """
        ...
