"""
Implement adaptable Color Representations combined in ColorBox

MOVE TO RICH ADAPTER:
Provide low-level helpers to generate Rich-compatible markup strings,
including color palettes, text styles, and ready-to-use colorizers.

"""

__all__: list[str] = [
    "ColorBox",
    "ColorStack",  # TODO:
]

from .box import ColorBox
