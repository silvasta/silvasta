"""
Funtcions, Callables and Checks

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "Calling",
    "ClassRendering",
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
    """Define the Shape of a Callable with Name"""

    @property
    def __name__(self) -> str: ...
    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out: ...


_test: _Callable = Calling


#  LINE: -- builtin views -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@runtime_checkable
class Stringable(Protocol):
    def __str__(self) -> str: ...


@runtime_checkable
class LogStringable(Protocol):
    def __repr__(self) -> str: ...


#  TASK: -- find proper separation/pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@runtime_checkable
class Normalizing(Protocol):
    def __call__(self, text: Any) -> Stringable:
        """Forward text-like object after processing and ensuring string"""


@runtime_checkable
class Sanitize[ExpectedT, UnexpectedT, TargeT](Protocol):
    def __call__(self, target: ExpectedT | UnexpectedT) -> TargeT:
        """Forward object after processing and ensuring types"""


@runtime_checkable
class NormalizingMaybe[ExpectedT: Stringable](
    Sanitize[ExpectedT, Any, Stringable], Protocol
):
    """Forward text after processing and ensuring string(able)"""


@runtime_checkable
class Colorizing(Protocol):
    def __call__(self, text: Stringable) -> str:
        # IDEA: def __call__(self, text: Stringable) -> Stringable:
        # - or some other renderable type
        """Forward text-like object after processing and ensuring string"""


#  LINE: -- processing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@runtime_checkable
class Listening[T](Protocol):
    def __call__(self, target: T) -> T:
        """Forward target after routing and inspection"""


@runtime_checkable
class ClassRendering(Protocol):
    def __call__(self, cls: type) -> str:
        """Process Classes like if they where Instances (e.g StaticFuncMeta)"""


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
