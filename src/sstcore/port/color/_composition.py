"""
Compose the Shape of the ColorBox

-
"""

from typing import Protocol

from ._definitions import SHORTCUTS, ColorPalette


class ColoBox(Protocol):
    """Provide Simple and Fast Color Supply"""

    shortcuts: dict[str, ColorPalette] = SHORTCUTS
