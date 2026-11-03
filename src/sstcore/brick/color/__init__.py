"""
Control the Colors and distribute the Paint

- colorize: ready-to-use functional stack
V
                                                 DependencyLevel[3]
                                                           vault(2)
"""

# TODO: DependencyLevel

__all__: list[str] = [
    "colorize",
    "SEMANTIC",  # CHECK: why here, not color.box.__init__?
]
from . import _colorize as colorize
from ._mappings import SEMANTIC
