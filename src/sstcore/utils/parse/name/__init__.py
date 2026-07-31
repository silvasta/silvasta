"""
Format and Parse Names in both directions

                                                       DependencyLevel[0]
"""

# STRATEGY: Move Package to sstcore.format!
# - This is dependency of sstcore.utils.view,
#   and potential from sstcore.error

__all__: list[str] = [
    # base
    "NamePattern",
    "NameParser",
    # implementations
    "ColoredName",
    "ParsedName",
    "SchemaName",
    # experimental
    "Name",
]

from ._base import (
    NameParser,
    NamePattern,
)
from ._colored import ColoredName
from ._name import Name
from ._parsed import ParsedName
from ._schema import SchemaName
