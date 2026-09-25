"""
Format and Parse Names in both directions

                                                       DependencyLevel[0]
"""

# IMPORTANT: think about location
# - makes brick.format not a functional stack anymore
# - acts more like a functor -> forge.func?
# WARNING: intended as supplier for Views:
# - maybe not supply brick.views but forge.view?
# - think about when and where the ColoredName should interact!

__all__: list[str] = [
    # base and core
    "NamePattern",
    "NameParser",
    # implementations
    "ColoredName",
    # experimental
    "StrName",
]

from ._colored import ColoredName
from ._core import NameParser, NamePattern
from ._str import Name as StrName
