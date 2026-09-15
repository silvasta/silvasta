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

"""
# NEXT: Hybrid as extension?

from collections.abc import Callable
from enum import StrEnum
from typing import (
    Any,
    Concatenate,
    Protocol,
    TypedDict,
    Unpack,
    overload,
    runtime_checkable,
)

__all__: list[str] = [
    "Functor",
    "SafeFunctorial",
    "ErrorPolicy",
]


class Functor1[**ArgSpace, SubSetResult](Protocol):
    """Dictate the Basic Requirements"""

    __name__: str
    __qualname__: str
    _func: Callable[ArgSpace, SubSetResult]

    def __call__(
        self, *args: ArgSpace.args, **kwargs: ArgSpace.kwargs
    ) -> SubSetResult: ...

    def emit(self, **kwargs: Any) -> None:
        """Provide default message sending"""


class Functor2[**ArgSpace, SubSetResult](Protocol):
    """Dictate the Basic Requirements"""

    __name__: str
    __qualname__: str
    _func: Callable[ArgSpace, SubSetResult]

    def __call__(self, *args, **kwargs): ...

    def emit(self, **kwargs: Any) -> None:
        """Provide default message sending"""


class BindFunctor1[**FreeArgs, **BoundArgs, SubSetResult](
    Functor1[BoundArgs, SubSetResult], Protocol
):
    # AI: something like this below... at the end the call must receive the reduced arg space and the func the regular
    # ├╴  Bare ParamSpec `FreeArgs` is not valid in this context in a type expression
    _func: Callable[Concatenate[FreeArgs, BoundArgs], SubSetResult]

    def __call__(
        self, *args: BoundArgs.args, **kwargs: BoundArgs.kwargs
    ) -> SubSetResult: ...


class BindFunctor2[**ArgSpace, **BoundArgs, SubSetResult](Functor2, Protocol):
    _func: Callable[ArgSpace, SubSetResult]

    def __call__(
        self, *args: BoundArgs.args, **kwargs: BoundArgs.kwargs
    ) -> SubSetResult: ...


class DiverseFunctor1[**ArgSpace, SubSetResult, SuperSetResult](
    Functor1, Protocol
):
    _func: Callable[ArgSpace, SubSetResult]

    def __call__(
        self, *args: ArgSpace.args, **kwargs: ArgSpace.kwargs
    ) -> SuperSetResult: ...


class DiverseFunctor11[**ArgSpace, SubSetResult, SuperSetResult](
    Functor1[ArgSpace, SuperSetResult], Protocol
):
    _func: Callable[ArgSpace, SubSetResult]

    def __call__(
        self, *args: ArgSpace.args, **kwargs: ArgSpace.kwargs
    ) -> SuperSetResult: ...


class DiverseFunctor2[**ArgSpace, SubSetResult, SuperSetResult](
    Functor2, Protocol
):
    def __call__(
        self, *args: ArgSpace.args, **kwargs: ArgSpace.kwargs
    ) -> SuperSetResult: ...

    _func: Callable[ArgSpace, SubSetResult]


class BindDiverseFunctor1[
    **FreeArgs,
    **BoundArgs,
    SubSetResult,
    SuperSetResult,
](
    BindFunctor1[FreeArgs, BoundArgs, SubSetResult],
    DiverseFunctor1[BoundArgs, SubSetResult, SuperSetResult],
    Protocol,
): ...


class BindDiverseFunctor2[
    **FreeArgs,
    **BoundArgs,
    SubSetResult,
    SuperSetResult,
](
    DiverseFunctor2[FreeArgs, BoundArgs, SubSetResult],
    BindFunctor2[FreeArgs, BoundArgs, SubSetResult],
    Protocol,
): ...


#  INFO:  - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


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


class ErrorPolicy(StrEnum):  # TODO: Str? only Enum?
    LOG_AND_CONTINUE = "log"
    LOG_AND_EXIT = "exit"
    RE_RAISE = "raise"


class DecoFunctorial[**P, R](Protocol):  # REMOVE: when hybrid stands
    """Execute on top of other functions"""


@runtime_checkable
class HybridFunctorial1[In, Out, **P](Protocol):
    """Three-way: apply value, wrap function, delay with policy."""

    def apply(
        self, value: In, /, *args: P.args, **kwargs: P.kwargs
    ) -> Out: ...

    def wrap[**Fn](
        self, fn: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]: ...

    # AI: delay is missing but that is as well not always required
    # - another mixin? or just handle it somehow with the args?
    # meaning treat the decorator with inputs like: hybird() == hybrid ??

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
        self,
        target: None = None,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Callable[[Callable[..., In]], Callable[..., Out]]: ...


class HybridFunctorial2[**P, InputT, OutputT](Functorial, Protocol):
    @overload
    def __call__(self, target: InputT, /, **policy: Any) -> OutputT: ...
    @overload
    def __call__(
        self, target: Callable[P, InputT], /, **policy: Any
    ) -> Callable[P, OutputT]: ...
    @overload
    def __call__(
        self, /, **policy: Any
    ) -> Callable[[Callable[P, InputT]], Callable[P, OutputT]]: ...
    def __call__(
        self,
        target: Any = None,
        **policy: Any,
    ) -> Any: ...


class HybridPolicy(TypedDict, total=False):
    """Base policy to be extended by specific implementations."""


class HybridFunctorial3[Target, **P, R](Protocol):
    @overload
    def __call__(
        self, target: Target, /, **policy: Unpack[HybridPolicy]
    ) -> R: ...

    @overload
    def __call__(self, target: Callable[P, Target], /) -> Callable[P, R]: ...

    @overload
    def __call__(
        self, target: None = None, /, **policy: Unpack[HybridPolicy]
    ) -> Callable[[Callable[P, Target]], Callable[P, R]]: ...

    def __call__(
        self,
        target: Target | Callable[P, Target] | None = None,
        /,
        **policy: Unpack[HybridPolicy],
    ) -> Any: ...
