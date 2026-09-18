"""
Funtcions, Callables and Checks

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "Calling",
    "ClassRendering",
    "Stacking",
    # views
    "LogStringable",
    "Stringable",
    # adapter
    "Richable",
    "RichView",
    "PydanticModel",
]

from collections.abc import Callable as _Callable
from typing import Any, Protocol, runtime_checkable


class Calling[**In, Out](Protocol):
    @property
    def __name__(self) -> str: ...
    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out: ...


_test: _Callable = Calling


@runtime_checkable
class ClassRendering(Protocol):
    def __call__(self, cls: type) -> str:
        """Process Classes like if they where Instances (e.g StaticFuncMeta)"""


@runtime_checkable
class Stacking(Protocol):  # NEXT: colorbox and more
    def __getattr__(self, name: str) -> Stacking:
        """Stack Attributes on top of each other by attribute calls"""


@runtime_checkable
class Colorizing(Protocol):
    # TODO: at least one of:
    # - Sanitizing:Stringable->str (Formatting)
    # - Sanitizing:Any->Stringable (Sanitizing)
    # - Sanitizing:Any->str (Stringing)
    # NOTE: why not:
    # - Colorize
    # - Sanitize
    # - Normalize
    def __call__(self, text: Stringable) -> str:
        """Forward text-like object after processing and ensuring string"""


@runtime_checkable
class Listening[T](Protocol):
    # REMOVE: ?
    def __call__(self, target: T) -> T:
        """Forward target after routing and inspection"""


#  LINE: -- builtin views -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@runtime_checkable
class Stringable(Protocol):
    def __str__(self) -> str: ...


@runtime_checkable
class LogStringable(Protocol):
    def __repr__(self) -> str: ...


#  LINE: -- adapter -- -- - -- -- - -- -- - -- -- - -- -- - -- --

type Richable = RichView | _RichConsolable | str

# IDEA: combined runtime_checkable full richable protocol!


@runtime_checkable
class RichView(Protocol):
    def __rich__(self) -> Richable: ...


# IDEA: maybe to view, maybe copy and here with runtime_checkable
class _RichConsolable(Protocol):
    def __rich_console__(self):
        """Just extend the Renderable type"""


@runtime_checkable
class PydanticModel(Protocol):  # MOVE: but where?
    """Find BaseModels without importing them"""

    def __pydantic_validator__(self): ...
    def model_dump(self) -> dict[str, Any]: ...
