"""
Control the Colors and distribute the Paint

- colorize: ready-to-use functional stack
V
                                                 DependencyLevel[3]
                                                           vault(2)
"""

# STRATEGY: where to assemble the colorbox?

__all__: list[str] = [
    "colorize",  # WARN: unsure, maybe collect some color functions itself, but not more, assemble in forge!
]
from . import _colorize as colorize
