"""
Transform Strings with meaningful Content

- str -> str (usually)
                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "ansi",
    "case",
    "align",
    # IDEAS: forward from align: indent,pad?
]

from . import _align as align
from . import _ansi as ansi
from . import _case as case
