"""
Provide Colors as ultimate Color ToolBox

.
"""

# TODO: DependencyLevel

__all__: list[str] = [
    "Colors",
    "Paint",
    "ColorPalette",
    "ColorFactory",
    "ColorManager",
    "SHORTCUTS",  # CHECK: why here, not color.__init__?
]

from .._mappings import SHORTCUTS
from ._colors import Colors
from ._manager import ColorManager
from ._paint import ColorFactory, ColorPalette, Paint
