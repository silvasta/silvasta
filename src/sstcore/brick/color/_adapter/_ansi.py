"""
Adapt Color Codes to the ColorGrid

- Hex (RGB, later...)
- Ansi

"""

__all__: list[str] = [
    "AnsiPalette",
]

from enum import auto

from ....port.calling import Stringable
from ....port.color import ColorData, Palette
from ._base import ColorBlock, PaletteDTO


class AnsiPalette(Palette):
    CLI = auto()

    def data(self) -> ColorData:
        match self:
            case self.CLI:
                return PaletteDTO(func=apply_ansi, colors=ANSI)
        return type(self)(0).data()


def apply_ansi(text: Stringable, color: str = "\033[34m") -> str:
    return f"{color}{text}\033[0m"


ANSI = ColorBlock(
    green_="\033[32m",
    teal__="\033[38;5;37m",
    azure_="\033[36m",
    blue__="\033[34m",
    purple="\033[35m",
    red___="\033[31m",
    orange="\033[38;5;208m",
    yellow="\033[33m",
    white_="\033[37m",
    slate_="\033[90m",
    carbon="\033[38;5;235m",
    black_="\033[30m",
)
