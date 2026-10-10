"""
Adapt Rich Colors and Styles to the ColorGrid

-
"""

__all__: list[str] = [
    "RichPalette",
    "apply_rich",
    "rich_style",
    "rich_markup",
]

from enum import auto

from ....port.calling import Stringable
from ....port.color import Adapter, ColorData, Palette
from ._base import ColorBlock, PaletteDTO


class RichPalette(Palette):
    """Palettes available within the Code Adapter."""

    CLI1 = auto()

    def data(self) -> ColorData:
        match self:
            case self.CLI1:
                return PaletteDTO(func=apply_rich, colors=RICH1)
        return type(self)(0).data()

    @property
    def adapter(self) -> Adapter:
        return Adapter.ANSI


def apply_rich(text, color: Stringable = "", *modifier: Stringable):
    return rich_markup(text, rich_style(modifier, color))


def rich_markup(text: Stringable, style: Stringable = "bold"):
    return f"[{style}]{text}[/]" if style else text


def rich_style(color: Stringable, *modifier: Stringable):
    # LATER: handle background etc...
    return " ".join([str(m) for m in modifier] + [str(color)]).strip()


RICH1 = ColorBlock(
    green_="green",
    teal__="steel_blue1",
    azure_="cyan",
    blue__="blue",
    purple="medium_purple3",
    red___="red",
    orange="orange_red1",
    yellow="gold3",
    white_="white",
    slate_="grey70",
    carbon="grey30",
    black_="black",
)
