"""
Expand the Horizontal Dimensions of the Colors

-
"""

from typing import Protocol


class ColorSchema(Protocol):
    def __str__(self) -> str: ...
