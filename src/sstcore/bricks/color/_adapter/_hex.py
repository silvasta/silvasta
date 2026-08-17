"""
Adapt Color Codes to the ColorGrid

- Hex (RGB, later...)
- Ansi

"""

__all__: list[str] = [
    "HexPalette",
]

from enum import auto

from ....port.collections import Stringable
from ....port.color import ColorData, Palette
from ._base import ColorBlock, PaletteDTO


class HexPalette(Palette):
    MAIN = auto()

    def data(self) -> ColorData:
        match self:
            case self.MAIN:
                return PaletteDTO(
                    func=apply_hex_as_ansi,
                    colors=HEX_ALL,
                    name=str(self),
                )


def apply_hex_as_ansi(text: Stringable, token: str = "#33B1FF") -> str:
    r, g, b = int(token[1:3], 16), int(token[3:5], 16), int(token[5:7], 16)
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


HEX_ALL = (
    "#dfdfe0",
    "#282828",
    "#2563EB",
    "#25be6a",
    "#fad615",
    "#E11D48",
    "#60666d",
    "#2e2e2e",
    "#33B1FF",
    "#08bdba",
    "#FF8A00",
    "#7C3AED",
)

HEX_1 = ColorBlock(
    c0="#dfdfe0",
    c1="#282828",
    c2="#2563EB",
    c3="#25be6a",
    c4="#fad615",
    c5="#E11D48",
)
HEX_2 = ColorBlock(
    c0="#60666d",
    c1="#2e2e2e",
    c2="#33B1FF",
    c3="#08bdba",
    c4="#FF8A00",
    c5="#7C3AED",
)
