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
from ..forge.blueprint import FunctorMeta, FunctorMetaData
from ..format import cls_name, reflect
from ..none import Ghost

FunctorInput = FunctorMetaData()


# REMOVE: entire function after reflect.func resolved
def _set_names(self, name: str):
    if not name:  # IMPORTANT: where to apply reflect.func? probably Data
        name = reflect.func(self._func, default=f"{cls_name(self)}Unit")
    self.__name__ = name
    self.__qualname__ = name


class BaseFunctor[**Param, Result](metaclass=FunctorMeta, data=FunctorInput):
    """Ensure Requirements and close MRO forwarding"""

    def __init__(
        self,
        func: Callable[Param, Result] | None = None,
        name: str = "",  # WARN: when does this arrive?
        **kwargs,
    ):
        # IMPORTANT: ensure _func (or directly __call__)
        # AI_TASK: where is the best point to load this?
        # - why not just use it in __new__ and directly attach it as __call__?
        # - the dto provides the proper __call__ and the constructor assembles it
        # - with default_error for not injecting or overriding it
        #   (still crirical with the hybrid)
        self._func: Callable[Param, Result] = func

        # WARN: when happens this:
        # kwargs and self.emit("Unconsumed kwargs at BaseFunctor!", **kwargs)???
        # - most likely SstMeta is the proper place
        super().__init__()

    def __call__(self, *args, **kwargs):
        """Instance-Level Execution & Delayed Binding"""

        # NEXT: fix the different __call__
        # AI_TASK: ensure that the hybrid workflow with _func still works

        # Phase 2 of CASE 3: We received @MyFunctor(kwargs), now we get the function
        if getattr(self, "_func", None) is None:
            self._func = args[0]
            functools.update_wrapper(self, self._func)
            return self

        # FIX: why apply? why here in BaseFunctor?
        return self.apply(args[0], *args[1:], **kwargs)


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
    # class SafeFunctorMixin[**Param, Result](_GhostFunctor):
    __call__: Callable  # NOTE: toggle this while implementing
    """Protect the Execution, Hanldle Errors, everything able to customize"""

    # WARN: the issue is somehow that 1 FunctorType may have multiple instances,
    # - each with different requirements for policy or exit_code or catch
    # def __init__(
    #     self,
    #     catch: Callable[[Exception, Any], Result | None] | None = None,
    #     error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE,
    #     exit_code: int = 1,
    #     **kwargs,):
    #     self.catch: Callable[[Exception, Any], Result | None] | None = catch
    #     self.error_policy: ErrorPolicy = error_policy
    #     self.exit_code: int = exit_code
    #     super().__init__(**kwargs)

    def safe(
        self, *args: Param.args, **kwargs: Param.kwargs
    ) -> Result | None | NoReturn:
        """Execute Function in Safe Environment"""
        try:
            return self(*args, **kwargs)
        except Exception as error:
            # STRATEGY: either all to cls-dto, or directly to cls
            if catch_func := self.__class__._data.catch:
                return catch_func(self, error, *args, **kwargs)
            return self.on_error(error, *args, **kwargs)

    def result(
        self, *args: Param.args, **kwargs: Param.kwargs
    ) -> Result | NoReturn:
        # TODO: Needed? or just use __call__??
        # - maybe some overload?
        # - otherwise 1 small function here for more comfort is not bad
        """Ensure Result or Raise"""
        if (result := self.safe(*args, **kwargs)) is None:
            raise RuntimeError("Nonething is impossible...")
        return result

    def on_error(self, error: Exception, *_, **__) -> Any | NoReturn:
        """Handle Function fail by Policy if Catch is not defined"""

        # STRATEGY: either all to cls-dto, or directly to cls
        policy = self.__class__._data.policy
        exit_code = self.__class__._data.exit_code

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


# MOVE: some assembly? (when everything is done...)
class SafeFunctor[**P, R](SafeFunctorMixin[P, R], BaseFunctor[P, R]): ...


#  TESTING:  - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Detect[In](Protocol):
    def __call__(self, target: object) -> TypeGuard[In]: ...


class HybridFunctorMixin[In, Out, **P]:
    # class HybridFunctorMixin[In, Out, **P](_GhostFunctor):
    _func: Callable[Concatenate[In, P], Out]  # NOTE: toggle if needed
    emit: Callable
    """Dispatch only. Logic lives in _func / apply."""

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
