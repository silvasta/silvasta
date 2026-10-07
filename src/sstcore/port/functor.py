"""
Define the Shape of Functions as Objects as Functions

Functor: Extend function f to Functor F
- f(A) -> R
- F(A,E) -> S [S: subset of R]

Specifier: open output space (LSP violation)
- F(A) -> S [S superset of R]

Binder: close input space (LSP violation)
- F(B) -> S [B: subset of A]

Extensions:
- SafeFunctorial: Include error handling with policy
- TODO: Hybrid

                                    DependencyLevel.sstcore.port[0]
"""

__all__: list[str] = [
    "Functor",
    "SafeFunctorial",
    "ErrorPolicy",
]

from collections.abc import Callable
from enum import StrEnum
from typing import Any, Concatenate, NoReturn, Protocol, TypeGuard, overload


class FuncEmit(Protocol):
    def __call__(self, *args, **kwargs: Any) -> None:
        """Keep the place until proper Emit arrives here"""


class Functor[**ArgSpace, SubSetResult](Protocol):
    """Define the Basic Requirements for any Functor"""

    call: Callable[ArgSpace, SubSetResult]
    __name__: str
    __qualname__: str

    @property
    def emit(self) -> FuncEmit:
        """Provide default message sending"""

    def __call__(
        self, *args: ArgSpace.args, **kwargs: ArgSpace.kwargs
    ) -> SubSetResult: ...


class SafeFunctorial[**Param, Result](Protocol):
    """Execute Functions in Safe Environement"""

    catch: Callable[Concatenate[Exception, Param], Result | None] | None

    @property
    def error_policy(self) -> ErrorPolicy: ...
    @property
    def exit_code(self) -> int: ...

    def safe(
        self, *args: Param.args, **kwargs: Param.kwargs
    ) -> Result | None: ...


class ErrorPolicy(StrEnum):  # LATER: Str? only Enum?
    LOG_AND_CONTINUE = "log"
    LOG_AND_EXIT = "exit"
    RE_RAISE = "raise"


#  LINE: -- Hybrid -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class HybridFunctorial[In, Out, **P](Protocol):
    @overload
    def __call__(
        self, target: In, /, *args: P.args, **kwargs: P.kwargs
    ) -> Out: ...
    @overload
    def __call__[**Fn](
        self, target: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]: ...
    @overload
    def __call__(
        self, /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[..., In]], Callable[..., Out]]: ...

    def detect(self, target: object) -> TypeGuard[In]:
        """Check if target is direct function call"""

    def wrap[**Fn](
        self, fn: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]: ...

    def delay[**Fn](
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[Fn, In]], Callable[Fn, Out]]: ...

    def reject(self, fail: object, *args, **kwargs) -> NoReturn: ...
