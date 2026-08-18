import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, NoReturn

from loguru import logger

from ...bricks.view import view
from ...port.builder import Ghost
from ...port.functor import (
    DecoFunctorial,
    ErrorPolicy,
    Functorial,
    SafeFunctorial,
)
from ..format import cls_name, reflect

# TASK: check again typing, change Param/Result  or Ghost


@view.functor()
class FunctorCore[**Param, Result]:
    def __init__(
        self,
        func: Callable[Param, Result] | None = None,
        name: str = "",
        **kwargs,
    ):
        self._func: Callable[Param, Result] | None = func
        self.name: str = name or reflect.func(func, default=cls_name(self))
        kwargs and self.emit("Unconsumed kwargs at FunctorCore!", **kwargs)
        super().__init__()  # close the MRO forwarding

    def __call__(self, *args: Param.args, **kwargs: Param.kwargs) -> Result:
        if not self._func:
            raise NotImplementedError("Provide func or override __call__!")
        return self._func(*args, **kwargs)

    def emit(self, *args, **kwargs) -> None:
        """Provide default message sending"""
        logger.debug(*args, **kwargs)


if TYPE_CHECKING:
    _instance: Functorial = FunctorCore()
    _class: type[Functorial] = FunctorCore
    _GhostFunctor = FunctorCore
else:
    _GhostFunctor = Ghost


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Essentials
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class SafeFuncMixin[**Param, Result](_GhostFunctor):
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

    def result(
        self, *args: Param.args, **kwargs: Param.kwargs
    ) -> Result | NoReturn:
        """Provide Result or Raise on None"""
        if (result := self.safe(*args, **kwargs)) is None:
            raise RuntimeError("Nonething is impossible...")
        return result

    def on_error(self, error: Exception) -> None | NoReturn:
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
    _instance: SafeFunctorial = SafeFuncMixin()
    _class: type[SafeFunctorial] = SafeFuncMixin


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Extensions
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class DecoFuncMixin[**Param, Result](_GhostFunctor):  # TODO:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


if TYPE_CHECKING:
    _instance: DecoFunctorial = DecoFuncMixin()
    _class: type[DecoFunctorial] = DecoFuncMixin
