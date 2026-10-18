"""
Adapt Rich Colors and Styles to the ColorGrid

-
"""

from rich.console import Console

__all__: list[str] = [
    "RichPalette",
    "apply_rich",
    "rich_style",
    "rich_markup",
]

from enum import auto

from ....port.color import Adapter, ColorData, Palette
from ._base import ColorBlock, PaletteDTO

console = Console()


class RichPalette(Palette):
    """Palettes available within the Code Adapter."""

    CLI1 = auto()

    def data(self) -> ColorData:
        match self:
            case self.CLI1:
                return PaletteDTO(func=apply_rich, colors=RICH1)
        return type(self)(0).data()

    @property  # LATER: this on base, auto-connecting both
    def adapter(self) -> Adapter:
        return Adapter.ANSI


def printing(func):
    def wrapper(*args, **kwargs):
        # result = func(*args, **kwargs)
        # print()
        # print(*args, **kwargs)
        # print(func.__name__, "_", result)
        # console.print(func.__name__, "_", result)
        # # input()
        # print()
        return func(*args, **kwargs)

    return wrapper


@printing
def apply_rich(text, color: str = "", *modifier: str):
    return rich_markup(text, rich_style(color, *modifier))


@printing
def rich_markup(text: str, style: str = "bold"):
    return f"[{style}]{text}[/]" if style else text


@printing
def rich_style(color: str, *modifier: str):
    # LATER: handle background etc...
    # x =
    # print(f"{x=}")
    return " ".join([*modifier, color]).strip()


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

if __name__ == "__main__":
    print(apply_rich("test rich", "cyan"))
