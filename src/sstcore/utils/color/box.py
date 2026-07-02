from collections.abc import Callable
from typing import Protocol

from .palette import BASE_PALETTE, ColorName, Palette
from .style import TextStyle


class Stringable(Protocol):
    """Let objects with __str__ pass the ty check"""

    def __str__(self) -> str: ...


type Style = TextStyle | str


class ColorBox:
    """Provide Simple and Fast Color Supply"""

    def __call__(
        self, text: Stringable, color: ColorName | None = None
    ) -> str:
        """Wrap Text inside Color and Style markup if well defined"""

        if not (markup := self._markup(color)):  # for: (style=normal,color="")
            return str(text)  # because: Stringable -> str

        return f"[{markup}]{text}[/]"

    def _markup(self, color: ColorName | None) -> str:
        """Assemble style and color, strip to compact string or even empty"""

        return f"{self._style.to_rich()} {color or ''}".strip()

    def __init__(
        self,
        palette: Palette = BASE_PALETTE,
        style: Style = TextStyle.NORMAL,
        shortcuts: bool = True,
    ):
        """Build ColorBox with overridable defaults for Palette and Style"""
        self._palette: Palette = palette
        self._style: TextStyle = TextStyle(style)  # safe for TextStyle
        self._shortcuts_enabled: bool = shortcuts

    def switch(
        self,
        palette: Palette | None = None,
        style: Style | None = None,
        shortcuts: bool | None = None,
    ):
        """Attach new Palette or TextStyle to existing ColorBox or toggle shortcuts"""
        if palette is not None:
            self._palette: Palette = palette
        if style is not None:
            self._style: TextStyle = TextStyle(style)
        if shortcuts is not None:
            self._shortcuts_enabled: bool = shortcuts

    @property
    def palette(self) -> Palette:
        return self._palette

    @classmethod
    def bold(cls, palette: Palette = BASE_PALETTE):
        return cls(palette=palette, style=TextStyle.BOLD)

    @classmethod
    def dim(cls, palette: Palette = BASE_PALETTE):
        return cls(palette=palette, style=TextStyle.DIM)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Colors
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def cyan(self, text: Stringable) -> str:
        return self(text, self._palette.cyan)

    def red(self, text: Stringable) -> str:
        return self(text, self._palette.red)

    def green(self, text: Stringable) -> str:
        return self(text, self._palette.green)

    def yellow(self, text: Stringable) -> str:
        return self(text, self._palette.yellow)

    def blue(self, text: Stringable) -> str:
        return self(text, self._palette.blue)

    def magenta(self, text: Stringable) -> str:
        return self(text, self._palette.magenta)

    def purple(self, text: Stringable) -> str:
        return self(text, "purple")

    def white(self, text: Stringable) -> str:
        return self(text, self._palette.white)

    def black(self, text: Stringable) -> str:
        return self(text, self._palette.black)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Shortcuts
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def __getattr__(self, name: Stringable) -> Callable[[Stringable], str]:
        """Support Shortcuts when enabled by Flag"""

        use_short: bool = self._shortcuts_enabled

        def _empty(text: Stringable) -> str:
            """Prevent Attribute failures for toggled of shortcuts"""
            return str(text)

        match name:
            case "c":
                return self.cyan if use_short else _empty
            case "r":
                return self.red if use_short else _empty
            case "g":
                return self.green if use_short else _empty
            case "y":
                return self.yellow if use_short else _empty
            case "s":
                return self.purple if use_short else _empty
            case "w":
                return self.white if use_short else _empty

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )
