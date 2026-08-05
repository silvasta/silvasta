import sys

from loguru import logger

from ...port.functor import ErrorPolicy


class SafeExecutionMixin[**P, R]:
    """Cross-cutting resilience."""

    error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE
    exit_code: int = 1

    def safe_call(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return self(*args, **kwargs)
        except Exception as error:
            return self._handle_error(error, *args, **kwargs)

    def _handle_error(self, error: Exception, *args, **kwargs) -> R | None:
        logger.critical(f"{self} failed: {error}")

        match self.error_policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                logger.error(f"Original error: {error}")
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise


from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Self

from ...port.functor import ErrorPolicy
from ...utils.view import Cli, Log, Rich, Str, view  # WARN: import danger


@view(cli=Cli.PANEL, str=Str.NAME, rich=Rich.MODULE, log=Log.DEBUG)
class FunctorBase:
    name: str


class SafeMixin[**P, R]:
    """Cross-cutting resilience."""

    error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE
    exit_code: int = 1
    handle: Callable

    def safe(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return self(*args, **kwargs)
        except Exception as error:
            try:
                return self.handle(error, *args, **kwargs)
            except Exception:
                self._handler_fail(error, *args, **kwargs)

    def _handler_fail(self, error: Exception, *args, **kwargs) -> Any:
        logger.critical(f"{self} failed: {error}")

        match self.error_policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                logger.error(f"Original error: {error}")
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise


class EmitMixin[**P, R]:
    """Cross-cutting resilience."""

    send: Callable | None  # regular logs etc
    emit: Callable | None  # from Bus.Emitter


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Assembly
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# @dataclass(frozen=True, kw_only=True)
# class Functor1[**P, R](
#     SafeExecutionMixin[P, R],
#     FactoryMixin[P, R],
#     FunctorBase,
# ):
#     """Lightweight default for most handlers."""
#
#     func: Callable[P, R]
#     metadata: dict[str, Any] = field(default_factory=dict)
#
#     def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
#         return self.func(*args, **kwargs)


@dataclass(kw_only=True)
class Functor[**P, R](FunctorBase, SafeMixin[P, R]):
    """Lightweight default for most handlers."""

    func: Callable[P, R]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.func(*args, **kwargs)


@dataclass(kw_only=True)
class TransferStrategy[**P, R](Functor):
    @classmethod
    def from_func(
        cls,
        func: Callable[P, R],
        name: str = "Functor",
        error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE,
        handle: Callable | None = None,
        **metadata: Any,
    ) -> Self:
        return cls(
            func=func,
            name=name,
            handle=handle,
            error_policy=error_policy,
            **metadata,
        )
