"""
Provide ErrorHandler with Registry (and defaults)

                                                       DependencyLevel[2]
"""

__all__: list[str] = [
    "ErrorHandler",
    "ErrorRegistry",
    # TODO: Defaults/Presets
]
from ._handler import ErrorHandler
from ._registry import ErrorRegistry
