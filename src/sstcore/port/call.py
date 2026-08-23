"""
Functor - Define the Shape of Functions as Objects as Functions

Base:
- Functorial: Define the Core functionality
- SafeFunctorial: Control Errors with Handlers
  - ErrorPolicy: Decide the default behaviour

Extended: (TODO)
- EmitFunctorial: Report the Status
- DecoFunctorial: Act on Signatures

"""

from collections.abc import Callable
from enum import StrEnum
from typing import Concatenate, Protocol, runtime_checkable

from .view import Stringable

__all__: list[str] = [
    "Functorial",
    "SafeFunctorial",
    "ErrorPolicy",
    #
    "Stacking",
]


@runtime_checkable
class ClassRendering(Protocol):
    def __call__(self, cls: type) -> str: ...


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


class Stacking(Protocol):
    """Stack Attributes on top of each other by Functions"""

    def __getattr__(self, name: str) -> Stacking:
        """Add one layer of color or modifier and stack again..."""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Functor
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@runtime_checkable
class Functorial[**Param, Result](Protocol):
    """Combine values and functions to advanced executables"""

    @property
    def name(self) -> str: ...
    @property
    def emit(self, *args, **kwargs) -> None: ...

    def __call__(self, *args: Param.args, **kwargs: Param.kwargs) -> Result:
        """The Core of the entire Topic, override or inject _func"""


class SafeFunctorial[**Param, Result](Protocol):
    """Provide safe execution environement"""

    catch: Callable[Concatenate[Exception, Param], Result | None] | None

    def safe(self, *args: Param.args, **kwargs: Param.kwargs) -> Result | None:
        """Catch and handle"""

    @property
    def error_policy(self) -> ErrorPolicy: ...
    @property
    def exit_code(self) -> int: ...


class ErrorPolicy(StrEnum):  # TODO: Str? only Enum?
    LOG_AND_CONTINUE = "log"
    LOG_AND_EXIT = "exit"
    RE_RAISE = "raise"


class DecoFunctorial[**P, R](Protocol):
    """Execute on top of other functions"""
