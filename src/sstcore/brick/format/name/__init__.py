"""
Format and Parse Names in both directions

                                                       DependencyLevel[0]
"""

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
