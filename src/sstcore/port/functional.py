"""
Provide checks on Callables

So far:
- view
- registry
- undefined

"""

# REFACTOR: resolve or combine with Functor??

import sys
from typing import Protocol, runtime_checkable

from .view import Stringable


def python_is_latest() -> bool:  # MOVE: maybe to port.setup?
    return sys.version_info >= (3, 15)


@runtime_checkable
class Colorizing(Protocol):
    def __call__(self, text: Stringable) -> str:
        """Forward text-like object after processing and ensuring string"""


@runtime_checkable
class Listening[T](Protocol):  # REMOVE: ??
    def __call__(self, target: T) -> T:
        """Forward target after any further routing and inspection"""


class Stacking(Protocol):
    """Stack Colors and Attributes on top of each other and Functions"""

    def __getattr__(self, name: str) -> Stacking:
        """Add one layer of color or modifier and stack again..."""
