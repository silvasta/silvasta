"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

__all__: list[str] = [
    "BaseFunctor",
    "SafeFunctor",
    "HybridFunctor",
]


import functools
import sys
import typing as _t
from collections.abc import Callable
from typing import Any, Concatenate

from ...brick.field import PolicyField, RequiredField
from ...brick.field._strategy import morphing, strategy
from ...brick.labor import clsname, funcname
from ...port import functorial
from ...port.functorial import ErrorPolicy
from ...port.link import portlink
from ..engine.blueprint import FunctorMeta, FunctorMetaData

FunctorInput = FunctorMetaData()


@portlink(functorial.Functorial)  # RENAME: who is Functor?
class BaseFunctor[**Args, Result](metaclass=FunctorMeta, data=FunctorInput):
    """Ensure Requirements and close MRO forwarding"""

    call: Callable[Args, Result]
    emit: functorial._FuncEmit

    def __init__(
        self,
        call: Callable[Args, Result] | None = None,
        name: str = "",
        **kwargs,
    ):  # LATER: __inin_subclass__ from here?

        if call is not None:
            self.call: Callable[Args, Result] = call

        name: str = name or funcname(self.call, default=f"{clsname(self)}Unit")
        self.__name__: str = name
        self.__qualname__: str = name

        if kwargs:
            self.emit(f"Undestroyed kwargs: {kwargs!r}")

        super().__init__()

    def __call__(self, *args: Args.args, **kwargs: Args.kwargs) -> Result:
        return self.call(*args, **kwargs)


type _Catch[**A, R] = Callable[Concatenate[Exception, A], R | None]


@portlink(functorial.SafeFunctorial)
class SafeFunctor[**Args, Result](BaseFunctor[Args, Result]):
    """Protect the Execution, Hanldle Errors, everything able to customize"""

    policy = PolicyField(ErrorPolicy.LOG_AND_CONTINUE)
    exit_code = RequiredField(types=int, default=1)

    def __init__(self, catch: _Catch[Args, Result] | None = None, **kwargs):
        if catch is not None:
            # CHECK: if direct assing works at usage!
            # needed because of confusion below
            setattr(self, "catch", catch)  # noqa:B010
        super().__init__(**kwargs)

    def safe(
        self, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | None | _t.NoReturn:
        try:
            return self(*args, **kwargs)
        except Exception as error:
            self.catch(error, *args, **kwargs)

    @strategy
    def catch(
        self, error: Exception, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | None | _t.NoReturn:
        """Execute pure Policy if catch is not defined"""
        self.emit(
            f"{self} failed: {error}", level="CRITICAL", param=(args, kwargs)
        )
        match self.policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise error


#  LINE: -- Hybrid -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@portlink(functorial.HybridFunctorial)
class HybridFunctor[In, Out, **P](BaseFunctor[Concatenate[In, P], Out]):
    """Extend Call for Hybrid3 and use Init for Hybrid2"""

    def __init__(self, detect: functorial.Detect[In] | None, **kwargs):
        # IMPORTANT: where is Hybrid2??
        if detect is not None:
            setattr(self, "detect", detect)  # noqa:B010
        super().__init__(**kwargs)

    @strategy
    def detect(self, target: Any, /) -> _t.TypeGuard[In]:
        """Check if target is direct function call"""
        raise NotImplementedError("typing.TypeGuard needed to detect!", target)

    @strategy
    def wrap[**Fn](
        self, fn: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]:
        """Case 2: Decorator"""

        @functools.wraps(fn)
        def wrapper(*fn_args: Fn.args, **fn_kwargs: Fn.kwargs) -> Out:
            return self.call(fn(*fn_args, **fn_kwargs), *args, **kwargs)

        return wrapper

    @morphing
    def bind[**Fn](
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[Fn, In]], Callable[Fn, Out]]:
        """Case 3: Bind additional input to case 2"""
        return lambda fn: self.wrap(fn, *args, **kwargs)

    def reject(self, failed: Any, *args, **kwargs) -> _t.NoReturn:
        self.emit("Invalid Hybrid Usage", failed, *args, **kwargs)
        raise TypeError("Invalid Hybrid Usage")

    @_t.overload
    def __call__(
        self, target: In, /, *args: P.args, **kwargs: P.kwargs
    ) -> Out: ...
    @_t.overload
    def __call__[**Fn](
        self, target: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]: ...
    @_t.overload
    def __call__(
        self, /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[..., In]], Callable[..., Out]]: ...

    def __call__(
        self, target: Any = None, /, *args: P.args, **kwargs: P.kwargs
    ):
        """Hybrid triple dispatch"""

        if self.detect(target):
            return self.call(target, *args, **kwargs)

        if callable(target) and target is not type:
            return self.wrap(target, *args, **kwargs)

        if target is None:
            return self.bind(*args, **kwargs)

        self.reject(target)
