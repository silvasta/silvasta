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

                                                 DependencyLevel[0]
                                                 - NEW: (maybe)
                                                   - .attach
"""

from collections.abc import Callable
from enum import StrEnum
from typing import Any, Concatenate, Protocol, TypedDict, overload

__all__: list[str] = [
    "Functor",
    "SafeFunctorial",
    "ErrorPolicy",
]


class Functor[**ArgSpace, SubSetResult](Protocol):
    """Dictate the Basic Requirements for any Functor"""

    __name__: str
    __qualname__: str
    # IDEA: make _func public! why not? or descriptor? or from meta?
    _func: Callable[ArgSpace, SubSetResult]

    def __call__(  # TODO:
        self, *args: ArgSpace.args, **kwargs: ArgSpace.kwargs
    ) -> SubSetResult: ...

    def emit(self, **kwargs: Any) -> None:
        """Provide default message sending"""


#  INFO:  Safe Extension - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


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


#  INFO:  Hybrid Extension - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class HybridFunctorial[In, Out, **P](Protocol):
    def apply(
        self, value: In, /, *args: P.args, **kwargs: P.kwargs
    ) -> Out: ...

    def wrap[**Fn](
        self, fn: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]: ...

    def delay[**Fn](
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[Fn, In]], Callable[Fn, Out]]: ...

    # IDEA: delete entire __call__ here and instead, inject hybrid as _func!
    @overload
    def __call__(  # INFO: regular function
        self,
        target: In,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Out: ...

    @overload
    def __call__[**Fn](  # INFO: regular decorator
        self,
        target: Callable[Fn, In],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Callable[Fn, Out]: ...

    @overload
    def __call__(  # INFO: decorator with args
        self,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Callable[[Callable[..., In]], Callable[..., Out]]: ...


# REMOVE: or find purpose
class HybridPolicy(TypedDict, total=False):
    """Base policy to be extended by specific implementations."""


#  INFO:  LSP acrobatic - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class BindFunctor[**FreeArgs, **BoundArgs, SubSetResult](
    Functor[BoundArgs, SubSetResult], Protocol
):
    """Narrow the Input Space (LSP-unconform)"""

    # FIX: separate input space, but how?
    _func: Callable[[FreeArgs, BoundArgs], SubSetResult]

    def __call__(
        self, *args: BoundArgs.args, **kwargs: BoundArgs.kwargs
    ) -> SubSetResult: ...


class ExpandFunctor[**ArgSpace, SubSetResult, SuperSetResult](
    Functor[ArgSpace, SuperSetResult], Protocol
):
    """Extend the output Space (LSP-unconform)"""

    _func: Callable[ArgSpace, SubSetResult]

    def __call__(
        self, *args: ArgSpace.args, **kwargs: ArgSpace.kwargs
    ) -> SuperSetResult: ...


# FIX: or later on just drop inheritance or even any declaration
class TransformFunctor[**FreeArgs, **BoundArgs, SubSetResult, SuperSetResult](
    BindFunctor[FreeArgs, BoundArgs, SubSetResult],
    ExpandFunctor[BoundArgs, SubSetResult, SuperSetResult],
    Protocol,
): ...
