"""
Define the Shape of Functions as Objects as Functions

Functor: Extend function f to Functor F
- f(A) -> R
- F(A,E) -> S [S: subset of R]

Opener: specify output space (LSP violation)
- F(A) -> S [S superset of R]

Binder: close input space (LSP violation)
- F(B) -> S [B: subset of A]

Extensions:
  - SafeFunctor: Ensure error handling with policy
  - HybridFunctor: Act on functions and methods

                                    DependencyLevel.sstcore.port[1]+
"""

__all__: list[str] = [
    "Functorial",
    #
    "SafeFunctorial",
    "Catch",
    "ErrorPolicy",
    #
    "HybridFunctorial",
    "Detect",
    "Wrap",
    "Bind",
    "BoundWrapper",
]

import typing as _t
from collections.abc import Callable as _Callable

from .solid import PolicyEnum as _PolicyEnum


class _FuncEmit(_t.Protocol):  # REMOVE: when replacement arrives
    def __call__(self, *args, **kwargs) -> None:
        """Keep the place until proper Emit arrives here"""


class Functorial[**ArgSpace, SubSetResult](_t.Protocol):
    """Define the Basic Requirements for any Functor"""

    call: _Callable[ArgSpace, SubSetResult]
    __name__: str
    __qualname__: str

    @property
    def emit(self) -> _FuncEmit:
        """Provide default message sending"""

    def __call__(
        self, *args: ArgSpace.args, **kwargs: ArgSpace.kwargs
    ) -> SubSetResult: ...


#  LINE: -- Safe -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SafeFunctorial[**ArgSpace, SubSetResult](_t.Protocol):
    """Execute Functions in Safe Environment"""

    @property
    def catch(self) -> Catch[ArgSpace, SubSetResult]:
        """Handle Function fail by Policy"""

    @property
    def policy(self) -> ErrorPolicy:
        """Store the Rules for Decision taking"""

    @property
    def exit_code(self) -> int:
        """The sys.exit(Value)"""

    def safe(
        self, *args: ArgSpace.args, **kwargs: ArgSpace.kwargs
    ) -> SubSetResult | None | _t.NoReturn:
        """Establish the Frame for Safe Execution"""


class Catch[**ArgSpace, SubSetResult](_t.Protocol):
    def __call__(
        self,
        error: Exception,
        /,
        *args: ArgSpace.args,
        **kwargs: ArgSpace.kwargs,
    ) -> SubSetResult | None | _t.NoReturn:
        """Handle Function fail by Policy"""


class ErrorPolicy(_PolicyEnum):
    """Provide RuleName Shortcut and basic resolving"""

    LOG_AND_CONTINUE = "log"  # WARN: overrides zero?
    LOG_AND_EXIT = "exit"
    RE_RAISE = "raise"


#  LINE: -- Hybrid -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class HybridFunctorial[In, Out, **P](_t.Protocol):
    """Decorate Functions, Methods or direct Calls"""

    @property
    def detect(self) -> Detect[In]:
        """Identify direct call or function"""

    @property
    def wrap(self) -> Wrap[In, Out, P]:
        """Wire the Target ready to drop in"""

    @property
    def bind(self) -> Bind[In, Out, P]:
        """Bind the Target with additional Parameters"""

    def reject(self, fail: _t.Any, *args, **kwargs) -> _t.NoReturn:
        """Handle Target that failed in Dispatch"""

    @_t.overload
    def __call__(
        self, target: In, /, *args: P.args, **kwargs: P.kwargs
    ) -> Out: ...

    @_t.overload
    def __call__[**Fn](
        self, target: _Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> _Callable[Fn, Out]: ...

    @_t.overload
    def __call__(
        self, /, *args: P.args, **kwargs: P.kwargs
    ) -> BoundWrapper[In, Out]: ...

    def __call__(
        self, target: _t.Any = None, /, *args: P.args, **kwargs: P.kwargs
    ):
        """Dispatch __call__:

        - Case 1: directly call function
        - Case 2: decorat target function
        - Case 3: bind param to decorator
        """


class Detect[In](_t.Protocol):
    def __call__(self, target: _t.Any, /) -> _t.TypeGuard[In]:
        """Identify the Target - fulfils Type?"""


class Wrap[In, Out, **P](_t.Protocol):
    def __call__[**Fn](
        self, fn: _Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> _Callable[Fn, Out]:
        """Wire the Target ready to drop in"""


class Bind[In, Out, **P](_t.Protocol):
    def __call__(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> BoundWrapper[In, Out]:
        """Bind the Target with additional Parameters"""


class BoundWrapper[In, Out](_t.Protocol):
    def __call__[**Fn](
        self, fn: _Callable[Fn, In], /
    ) -> _Callable[Fn, Out]: ...
