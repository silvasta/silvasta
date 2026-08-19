"""
TEMPORARY STORAGE and Internal Color Schemas and Mappings

- SHORTCUTS: For limited space and fast access to colors
- SEMANTIC: Map by describing word

"""

__all__: list[str] = [
    "SHORTCUTS",
]

from ...port.color import Color

SHORTCUTS: dict[str, Color] = {
    "b": Color.BLUE,
    "g": Color.GREEN,
    "r": Color.RED,
    "y": Color.YELLOW,
    "a": Color.AZURE,
    "t": Color.TEAL,
    "o": Color.ORANGE,
    "p": Color.PURPLE,
    "w": Color.WHITE,
    "s": Color.SLATE,
    "c": Color.CARBON,
    "d": Color.BLACK,
}


SEMANTIC: dict[str, Color] = {
    "alert": Color.TEAL,
    "danger": Color.ORANGE,
    "error": Color.RED,
    "info": Color.WHITE,
    "special": Color.PURPLE,
    "success": Color.GREEN,
    "title": Color.AZURE,
}


_HEX_DICT_9717: dict[str, Color] = {  # NOTE: keep for now
    "#2563EB": Color.BLUE,
    "#25be6a": Color.GREEN,
    "#E11D48": Color.RED,
    "#fad615": Color.YELLOW,
    "#33B1FF": Color.AZURE,
    "#08bdba": Color.TEAL,
    "#FF8A00": Color.ORANGE,
    "#7C3AED": Color.PURPLE,
    "#dfdfe0": Color.WHITE,
    "#60666d": Color.SLATE,
    "#2e2e2e": Color.CARBON,
    "#282828": Color.BLACK,
}
