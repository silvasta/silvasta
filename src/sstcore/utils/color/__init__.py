"""
Collect Color and Style container and tools.

Provide low-level helpers to generate Rich-compatible markup strings,
including color palettes, text styles, and ready-to-use colorizers.

Key components:
    - Palette: predefined color mappings for semantic roles (info, warning, etc.)
    - TextStyle: enumerated text attributes (bold, dim, reverse)
    - ColorBox: thin facade to apply styles and colors to text
    - colorize: convenience functions for common formatting tasks

"""

__all__: list[str] = [
    "colorize",
    "ColorBox",
    "Palette",
]

from . import colorize
from .box import ColorBox
from .palette import Palette
