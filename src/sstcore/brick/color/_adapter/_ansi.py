"""
Adapt Color Codes to the ColorGrid

- Hex (RGB, later...)
- Ansi

"""

__all__: list[str] = [
    "AnsiPalette",
]

from enum import auto

from ....port.collections import Stringable
from ....port.color import ColorData, Palette
from ._base import CustomBlock, PaletteDTO, StandardBlock


class AnsiPalette(Palette):
    CLI = auto()

    def data(self) -> ColorData:
        match self:
            case self.CLI:
                return PaletteDTO(
                    func=apply_ansi,
                    colors=(ANSI_STANDARD + ANSI_CUSTOM),
                    name=str(self),
                )


def apply_ansi(text: Stringable, token: str = "\033[34m") -> str:
    return f"{token}{text}\033[0m"


ANSI_STANDARD = StandardBlock(
    white_="\033[37m",
    black_="\033[30m",
    blue__="\033[34m",
    green_="\033[32m",
    yellow="\033[33m",
    red___="\033[31m",
)

ANSI_CUSTOM = CustomBlock(
    slate_="\033[90m",
    carbon="\033[38;5;235m",
    azure_="\033[36m",
    teal__="\033[38;5;37m",
    orange="\033[38;5;208m",
    purple="\033[35m",
)
