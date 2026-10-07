"""
Implement the Functors for functions and more

- Pick and provide the best of OOP/FP

"""

import sys
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    NoReturn,
)

from loguru import logger

from ...brick.labor import clsname, funcname
from ...port.functor import ErrorPolicy, Functor, SafeFunctorial
from ...port.link import portlink

# AI: this file was the former implementation


@portlink(Functor)
class BaseFunctor[**Param, Result]:
    """Ensure Requirements and close MRO forwarding"""

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

    def _set_names(self, name: str):  # TASK: this to Meta?
        if not name:
            name: str = funcname(self._func, default=f"{clsname(self)}Unit")
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


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Essentials
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@portlink(SafeFunctorial)
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

    def result(
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
