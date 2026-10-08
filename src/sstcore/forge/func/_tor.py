"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

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


@portlink(functorial.SafeFunctorial)
class SafeFunctor[**Args, Result](BaseFunctor[Args, Result]):
    """Protect the Execution, Hanldle Errors, everything able to customize"""

    # AI: morphing
    # catch: Callable[Concatenate[Exception, Args], Result | None]

    policy = PolicyField(ErrorPolicy.LOG_AND_CONTINUE)
    exit_code = RequiredField(types=int, default=1)

    def __init__(
        self,
        catch: Callable[[Exception, Any], Result | None] | None = None,
        **kwargs,
    ):
        if catch is not None:
            # FIX: here the otherr case with broken self
            self.catch = catch  # ty:ignore
            # self.catch: Callable[[Exception, Any], Result | None] = catch
        super().__init__(**kwargs)

    def safe(  # IDEA: overload to super().__call__?? and this here @strategy
        self, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | None | _t.NoReturn:
        try:
            return self(*args, **kwargs)
        except Exception as error:
            self.catch(error, *args, **kwargs)  # ty:ignore FIX: broken self in @strategy

    @strategy
    def catch(self, error: Exception, *args, **kwargs) -> Any | _t.NoReturn:
        """Execute pure Policy if catch is not defined"""
        self.emit(
            f"{self} failed: {error}", level="CRITICAL", param=(args, kwargs)
        )
        match self.error_policy:  # ty:ignore FIX: broken self in @strategy
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
            self.detect: functorial.Detect = detect
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
    def bind(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[..., In]], Callable[..., Out]]:
        """Case 3: Bind additional input to case 2"""
        return lambda fn: self.wrap(fn, *args, **kwargs)

    def reject(self, failed: Any, *args, **kwargs) -> _t.NoReturn:
        self.emit("Invalid Hybrid Usage", failed, *args, **kwargs)
        raise TypeError("Invalid Hybrid Usage")  # TASK: FunctorError

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

        if self.detect(target):  # ty:ignore
            # FIX: why is self broken here???
            return self.call(target, *args, **kwargs)

        if callable(target) and target is not type:
            return self.wrap(target, *args, **kwargs)

        if target is None:
            return self.bind(*args, **kwargs)

        self.reject(target)
