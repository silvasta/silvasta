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
from ...port.link import portlink
from ..engine.blueprint import FunctorMeta, FunctorMetaData

FunctorInput = FunctorMetaData()


@portlink(Functor)
class BaseFunctor[**Param, Result](metaclass=FunctorMeta, data=FunctorInput):
    """Ensure Requirements and close MRO forwarding"""

    def __init__(
        self,
        func: Callable[Param, Result] | None = None,
        name: str = "",  # WARN: when does this arrive?
        **kwargs,
    ):
        self._func: Callable[Param, Result] = func

        super().__init__()

    def __call__(self, *args, **kwargs):
        """Instance-Level Execution & Delayed Binding"""

        # Phase 2 of CASE 3: We received @MyFunctor(kwargs), now we get the function
        if getattr(self, "_func", None) is None:
            self._func = args[0]
            functools.update_wrapper(self, self._func)
            return self

        # FIX: why apply? why here in BaseFunctor? better override _func there?
        return self.apply(args[0], *args[1:], **kwargs)


if TYPE_CHECKING:
    _instance: Functor = BaseFunctor()
    _class: type[Functor] = BaseFunctor


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Essentials
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@portlink(SafeFunctorial)
class SafeFunctorMixin[**Param, Result]:
    # __call__: Callable  # NOTE: toggle this while implementing
    """Protect the Execution, Hanldle Errors, everything able to customize"""

    # WARN: the issue is somehow that 1 FunctorType may have multiple instances,
    # - each with different requirements for policy or exit_code or catch
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
            # STRATEGY: either all to meta-dto, or directly to cls
            if catch_func := self.__class__._data.catch:
                return catch_func(self, error, *args, **kwargs)
            return self.on_error(error, *args, **kwargs)

    def on_error(self, error: Exception, *_, **__) -> Any | NoReturn:
        """Handle Function fail by Policy if Catch is not defined"""

        # STRATEGY: either all to meta-dto, or directly to cls
        policy: ErrorPolicy = self.__class__._data.policy
        exit_code: int = self.__class__._data.exit_code

        logger.critical(f"{self} failed: {error}")

        match policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                logger.error(f"Original error: {error}")
                sys.exit(exit_code)

            case ErrorPolicy.RE_RAISE:
                raise error


if TYPE_CHECKING:
    _instance: SafeFunctorial = SafeFunctorMixin()
    _class: type[SafeFunctorial] = SafeFunctorMixin


@portlink(SafeFunctorial)
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


@portlink(HybridFunctorial)
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
