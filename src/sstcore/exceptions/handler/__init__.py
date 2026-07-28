"""
Provide ErrorHandler with Registry

                                                          PackageLevel[1]
"""

__all__: list[str] = [
    # TODO: Defaults
    "ErrorHandler",
    "ErrorRegistry",
]
from ._handler import ErrorHandler
from ._registry import ErrorRegistry
