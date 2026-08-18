"""
Provide checks on Callables

So far:
- view
- registry
- undefined

"""

__all__: list[str] = [
    "Colorizing",
]

import sys
from typing import Protocol, runtime_checkable

from .view import Stringable

# REFACTOR: resolve or combine with ...??


def python_is_latest() -> bool:  # MOVE: maybe to port.setup?
    """Short attempt to dispatch Lazy Imports: Python 3.15->14..."""
    return sys.version_info >= (3, 15)


@runtime_checkable
class Colorizing(Protocol):  # TODO: Sanitizing:Stringable->str
    def __call__(self, text: Stringable) -> str:
        """Forward text-like object after processing and ensuring string"""


@runtime_checkable
class Listening[T](Protocol):  # MOVE: emit??
    def __call__(self, target: T) -> T:
        """Forward target after any further routing and inspection"""


class Stacking(Protocol):  # TODO: general for not only Painters
    """Stack Colors and Attributes on top of each other and Functions"""

    def __getattr__(self, name: str) -> Stacking:
        """Add one layer of color or modifier and stack again..."""
