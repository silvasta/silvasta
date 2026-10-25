"""
Build the Functor for the Exception handling

                             DependencyLevel.sstcore.error.catch[0]
"""

__all__: list[str] = [
    "ErrorHandler",
]

import inspect
from collections.abc import Callable
from typing import Self, Unpack, get_type_hints

from ...brick.field._strategy import StrategyField
from ...brick.reflect import clsname, funcname
from ...forge.func import SafeFunctor
from ...forge.func._safe import SafeFunctorInput
from ...port.functorial import ErrorPolicy


class ErrorHandler[Error: BaseException](SafeFunctor[[Error], None]):
    """Handle CLI Exception and Terminate"""

    def __init__(
        self, error_type: type[Error], **kwargs: Unpack[SafeFunctorInput]
    ):
        self.error_type: type[Error] = error_type
        super().__init__(**kwargs)

    def _format_name(self, name: str = "") -> str:
        """Format str:= [(Cls)][{name}::{error}]"""
        return f"{name or super()._format_name()}::{clsname(self.error_type)}"

    def handles(self, error: BaseException, /) -> bool:
        """Check whether this handler is responsible for the given exception."""
        return isinstance(error, self.error_type)

    @StrategyField(bind_to_self=False)
    def _call(self, error: Error) -> None:
        self._emit(
            f"Unhandled {clsname(error)}: {error}",
            level="ERROR",
            exception=error,
        )

    @classmethod
    def from_func(
        cls,
        func: Callable[[Error], None],
        *,
        exit_code: int = 1,
        policy: ErrorPolicy = ErrorPolicy.LOG_AND_EXIT,
        name: str = "",
    ) -> Self:
        """Build ErrorHandler by inferring the Exception type from the first parameter."""

        if not (params := list(inspect.signature(func).parameters.values())):
            raise TypeError(f"Cannot infer error_type: {funcname(func)}")

        if not _is_valid(error_type := _find_error_type(func, params[0])):
            raise TypeError(
                f"First parameter '{params[0].name}' of '{funcname(func)}' "
                f"must be annotated with a BaseException subclass, got {error_type!r}."
            )
        return cls(
            error_type=error_type,
            call=func,
            exit_code=exit_code,
            policy=policy,
            name=name or funcname(func, default="CustomErrorHandler"),
        )


def _is_valid(_error_type):
    return (
        _error_type is not inspect.Parameter.empty
        and isinstance(_error_type, type)
        and issubclass(_error_type, BaseException)
    )


def _find_error_type(func: Callable, param, /):
    _hints = get_type_hints(func)
    return _hints.get(param.name, param.annotation)
