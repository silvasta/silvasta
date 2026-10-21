"""
Implement the Connection to the Adapter and Schemas

-
"""

__all__: list[str] = [
    "RichPalette",
    "AnsiPalette",
    "HexPalette",
    #
    "get_palette",
    "PaletteDTO",
]


from ....port.color import Adapter, Palette
from ._ansi import AnsiPalette
from ._base import PaletteDTO
from ._hex import HexPalette
from ._rich import RichPalette


def get_palette(adapter: Adapter) -> type[Palette]:
    """Link the base Adapter to the specific Palette"""

    match adapter:
        case Adapter.RICH:
            return RichPalette
        case Adapter.ANSI:
            return AnsiPalette
        case Adapter.HEX:
            return HexPalette
        case _:
            raise ValueError(f"Missing Adapter or Palette! {adapter!r}")
