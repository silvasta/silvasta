"""
TEMPORARY STORAGE and Internal Color Schemas and Mappings

- SHORTCUTS: For limited space and fast access to colors
- SEMANTIC: Map by describing word

"""

__all__: list[str] = [
    "SHORTCUTS",
]

from ...port.color import Color

# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:

SHORTCUTS: dict[str, Color] = {
    "a": Color.AZURE,
    "b": Color.BLUE,
    "c": Color.CARBON,
    "d": Color.BLACK,
    "g": Color.GREEN,
    "o": Color.ORANGE,
    "p": Color.PURPLE,
    "r": Color.RED,
    "s": Color.SLATE,
    "t": Color.TEAL,
    "w": Color.WHITE,
    "y": Color.YELLOW,
}

SEMANTIC: dict[str, Color] = {
    "alert": Color.YELLOW,
    "danger": Color.ORANGE,
    "dark": Color.CARBON,
    "error": Color.RED,
    "info": Color.WHITE,
    "night": Color.BLACK,
    "path": Color.BLUE,
    "shadow": Color.SLATE,
    "special": Color.PURPLE,
    "success": Color.GREEN,
    "title": Color.AZURE,
    "warn": Color.TEAL,
}

_SHORTCUTS: dict[str, Color] = {
    "a": Color.AZURE,
    "b": Color.BLUE,
    "c": Color.CARBON,
    "n": Color.BLACK,
    "g": Color.GREEN,
    "o": Color.ORANGE,
    "p": Color.PURPLE,
    "r": Color.RED,
    "s": Color.SLATE,
    "t": Color.TEAL,
    "w": Color.WHITE,
    "y": Color.YELLOW,
}


_HEX_DICT_9776: dict[str, Color] = {
    "#25be6a": Color.GREEN,
    "#08bdba": Color.TEAL,
    "#33B1FF": Color.AZURE,
    "#2563EB": Color.BLUE,
    "#7C3AED": Color.PURPLE,
    "#E11D48": Color.RED,
    "#FF8A00": Color.ORANGE,
    "#fad615": Color.YELLOW,
    "#e3e3e3": Color.WHITE,
    "#b5b5b5": Color.CARBON,
    "#4a4a4a": Color.SLATE,
    "#1c1c1c": Color.BLACK,
}

_HEX_DICT_9717: dict[str, Color] = {
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
