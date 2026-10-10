"""
Adapt Color Codes to the ColorGrid

- Hex (RGB, later...)
- Ansi

"""

__all__: list[str] = [
    "HexPalette",
]

from enum import auto

from ....port.calling import Stringable
from ....port.color import ColorData, Palette
from ._base import ColorBlock, PaletteDTO


class HexPalette(Palette):
    CLI = auto()

    def data(self) -> ColorData:
        match self:
            case self.CLI:
                return PaletteDTO(func=apply_hex_as_ansi, colors=HEX)
        return type(self)(0).data()


def apply_hex_as_ansi(text: Stringable, color: str = "#33B1FF") -> str:
    _r, _g, _b = (
        int(color[1:3], base=16),
        int(color[3:5], base=16),
        int(color[5:7], base=16),
    )
    return f"\033[38;2;{_r};{_g};{_b}m{text}\033[0m"


HEX = ColorBlock(
    "#25be6a",
    "#08bdba",
    "#33B1FF",
    "#2563EB",
    "#7C3AED",
    "#E11D48",
    "#FF8A00",
    "#fad615",
    "#e3e3e3",
    "#b5b5b5",
    "#4a4a4a",
    "#1c1c1c",
)
