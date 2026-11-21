"""
Format and Parse Names in both directions

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "ColoredName",
    "StrName",
]

from ._colored import ColoredName
from ._str import Name as StrName
