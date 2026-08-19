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

from ....port.collections import Stringable
from ....port.color import Adapter, ColorData, Palette
from ._base import CustomBlock, PaletteDTO, StandardBlock


class RichPalette(Palette):
    """Palettes available within the Code Adapter."""

    CLI1 = auto()

    def data(self) -> ColorData:
        match self:
            case self.CLI1:
                return PaletteDTO(
                    func=apply_rich,
                    colors=(RICH_STANDARD + RICH_CUSTOM),
                    name=str(self),
                )

    @property
    def adapter(self) -> Adapter:
        return Adapter.ANSI


def apply_rich(text, color: Stringable = "", modifier: Stringable = ""):
    return rich_markup(text, rich_style(modifier, color))


def rich_markup(text: Stringable, style: Stringable = "bold"):
    return f"[{style}]{text}[/]" if style else text


def rich_style(modifier: Stringable, color: Stringable):
    f"{modifier} {color}".strip()  # LATER: the ..on.. background?


RICH_STANDARD = StandardBlock(
    white_="white",
    black_="black",
    blue__="blue",
    green_="green",
    yellow="gold3",
    red___="red",
)

RICH_CUSTOM = CustomBlock(
    slate_="grey70",
    carbon="grey30",
    azure_="cyan",
    teal__="steel_blue1",
    orange="orange_red1",
    purple="medium_purple3",
)
