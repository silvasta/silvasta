"""
TEMPORARY separatet from .call

- better workflow at functor operation
"""

from typing import (
    Protocol,
    runtime_checkable,
)

__all__: list[str] = [
    "Stacking",
    "ClassRendering",
]


@runtime_checkable
class ClassRendering(Protocol):
    def __call__(self, cls: type) -> str:
        """Process Classes like if they where Instances (e.g StaticFuncMeta)"""


class Stacking(Protocol):
    def __getattr__(self, name: str) -> Stacking:
        """Stack Attributes on top of each other by attribute calls"""


#  REFACTOR:  - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Stringable(Protocol):  # TODO: check with view
    def __str__(self) -> str: ...


@runtime_checkable
class Colorizing(Protocol):
    # TODO: at least one of:
    # - Sanitizing:Stringable->str (Formatting)
    # - Sanitizing:Any->Stringable (Sanitizing)
    # - Sanitizing:Any->str (Stringing)
    def __call__(self, text: Stringable) -> str:
        """Forward text-like object after processing and ensuring string"""


@runtime_checkable
class Listening[T](Protocol):
    def __call__(self, target: T) -> T:
        """Forward target after routing and inspection"""
