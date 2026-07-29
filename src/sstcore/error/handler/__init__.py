"""
Provide ErrorHandler with Registry (and defaults)

                                                       DependencyLevel[2]
"""

__all__: list[str] = [
    # TODO: Defaults
    "ErrorHandler",
    "ErrorRegistry",
]
from ._handler import ErrorHandler
from ._registry import ErrorRegistry
