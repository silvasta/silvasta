"""
Implement the Functors for functions and more

- Pick and provide the best of OOP/FP

"""

import functools
import sys
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    NoReturn,
    Protocol,
    TypeGuard,
)

from loguru import logger

from ...port.functor import (
    ErrorPolicy,
    Functor,
    HybridFunctorial,
    SafeFunctorial,
)
from ..format import clsname, reflect
from ..none import Ghost


class BaseFunctor[**Param, Result]:
    """Ensure Requirements and close MRO forwarding"""

    # IDEA: all relevant functions, inject in __init__ Or override, or defaults
    # -> looks like it can be solved once in meta, then work everywhere!
    # - here: func, maybe init

    def __init__(
        self,
        func: Callable[Param, Result] | None = None,
        name: str = "",
        **kwargs,
    ):
        self._func: Callable[Param, Result] | None = func
        self._set_names(name)
        kwargs and self.emit("Unconsumed kwargs at BaseFunctor!", **kwargs)
        super().__init__()

    def _set_names(self, name: str):
        # TASK: this to Meta
        if not name:
            name = reflect.func(self._func, default=f"{clsname(self)}Unit")
        self.__name__: str = name
        self.__qualname__: str = name

    def __call__(self, *args: Param.args, **kwargs: Param.kwargs) -> Result:
        # IDEA: instead of override this, override BaseFunctor.func?
        if not self._func:
            raise NotImplementedError("Provide func or override __call__!")
        return self._func(*args, **kwargs)

    def emit(self, *args, **kwargs) -> None:  # LATER: override or inject?
        logger.debug(*args, **kwargs)


if TYPE_CHECKING:
    _instance: Functor = BaseFunctor()
    _class: type[Functor] = BaseFunctor
    _GhostFunctor = BaseFunctor
else:
    _GhostFunctor = Ghost  # NOTE: toggle this while implementing in class


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Essentials
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class SafeFunctorMixin[**Param, Result]:
    __call__: Callable  # NOTE: toggle this while implementing

    # IDEA: all relevant functions, inject in __init__ Or override, or defaults
    # - here: catch

    def __init__(
        self,
        catch: Callable[[Exception, Any], Result | None] | None = None,
        error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE,
        exit_code: int = 1,
        **kwargs,
    ):
        self.catch: Callable[[Exception, Any], Result | None] | None = catch
        self.error_policy: ErrorPolicy = error_policy
        self.exit_code: int = exit_code
        super().__init__(**kwargs)

    def safe(
        self, *args: Param.args, **kwargs: Param.kwargs
    ) -> Result | None | NoReturn:
        """Execute Function in Safe Environment"""
        try:
            return self(*args, **kwargs)
        except Exception as error:
            if self.catch:
                return self.catch(error, *args, **kwargs)
            return self.on_error(error, *args, **kwargs)

    def result(  # TODO: Needed? or just use __call__??
        self, *args: Param.args, **kwargs: Param.kwargs
    ) -> Result | NoReturn:
        """Provide Result or Raise on None"""
        if (result := self.safe(*args, **kwargs)) is None:
            raise RuntimeError("Nonething is impossible...")
        return result

    def on_error(self, error: Exception, *_, **__) -> Any | NoReturn:
        """Handle Function fail by Policy if Catch is not defined"""
        logger.critical(f"{self} failed: {error}")

        match self.error_policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                logger.error(f"Original error: {error}")
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise error


if TYPE_CHECKING:
    _instance: SafeFunctorial = SafeFunctorMixin()
    _class: type[SafeFunctorial] = SafeFunctorMixin


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Extensions
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# MOVE: some assembly? (when everything is done...)
class SafeFunctor[**P, R](SafeFunctorMixin[P, R], BaseFunctor[P, R]): ...


#  TESTING:  - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Detect[In](Protocol):
    def __call__(self, target: object) -> TypeGuard[In]: ...


class HybridFunctorMixin[In, Out, **P](_GhostFunctor):
    """Dispatch only. Logic lives in _func / apply."""

    # IDEA: all relevant functions, inject in __init__ Or override, or defaults
    # - here:
    #   - main: apply,wrap,delay
    #   - why not: detect,reject

    # _func: Callable[Concatenate[In, P], Out] # NOTE: toggle if needed
    detect: Detect[In]

    def detect(self, target: object) -> TypeGuard[In]:
        raise NotImplementedError("Need TypeGuard to detect!", target)

    def reject(self, fail: object, *args, **kwargs) -> NoReturn:
        # LATER: improve, use from ._hybrid
        self.emit("Invalid Hybrid Usage", fail, *args, **kwargs)
        raise TypeError("Invalid Hybrid Usage")

    def __call__(
        self,
        target: object = None,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> object:
        """Hybrid triple dispatch"""

        if self.detect(target):
            return self.apply(target, *args, **kwargs)

        if callable(target) and target is not type:
            return self.wrap(target, *args, **kwargs)

        if target is None:
            return self.delay(*args, **kwargs)

        self.reject(target)

    def apply(self, value: In, /, *args: P.args, **kwargs: P.kwargs) -> Out:
        """Case 1: Function"""
        if not self._func:  # IDEA: super().__call__??
            raise NotImplementedError("Provide func or override __call__!")
        return self._func(value, *args, **kwargs)

    def wrap[**Fn](
        self, fn: Callable[Fn, In], /, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[Fn, Out]:
        """Case 2: Decorator"""

        @functools.wraps(fn)
        def wrapper(*fn_args: Fn.args, **fn_kwargs: Fn.kwargs) -> Out:
            return self.apply(fn(*fn_args, **fn_kwargs), *args, **kwargs)

        return wrapper

    def delay(
        self, *args: P.args, **kwargs: P.kwargs
    ) -> Callable[[Callable[..., In]], Callable[..., Out]]:
        """Case 3: Bind additional input to case 2"""
        # TODO: check how well the parametrization works with that
        return lambda fn: self.wrap(fn, *args, **kwargs)


# MOVE: some assembly?
class HybridFunctor[In, Out, **P](
    HybridFunctorMixin[In, Out, P],
    BaseFunctor[Concatenate[In, P], Out],
):
    def __init__(  # REMOVE: ??
        # IDEA: inject hybrid here?? as func!!
        self,
        func: Callable[Concatenate[In, P], Out],
        *,
        detect: Detect[In],
        reject: Callable[[object], NoReturn],
        name: str = "",
        **kwargs,
    ):
        # REFACTOR: maybe a generalized inject/override? in Meta?? MetaData?
        self.detect = detect
        self.reject = reject
        super().__init__(func=func, name=name, **kwargs)


if TYPE_CHECKING:
    _instance: HybridFunctorial = HybridFunctorMixin()
    _class: type[HybridFunctorial] = HybridFunctorMixin
    #
    _instance: Functor = HybridFunctorMixin()  # needed?
    _class: type[Functor] = HybridFunctorMixin  # needed?
