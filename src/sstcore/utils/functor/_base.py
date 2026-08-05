import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from loguru import logger

from ...port.functor import ErrorPolicy
from ...utils.view import Cli, Log, Rich, Str, view  # WARN: import danger


@view(cli=Cli.PANEL, str=Str.NAME, rich=Rich.MODULE, log=Log.DEBUG)
class _View: ...


@dataclass
class Functor[**P, R](_View):
    func: Callable[P, R]
    name: str
    handle: Callable | None
    error_policy: ErrorPolicy
    exit_code: int = 1
    emit: Callable | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.func(*args, **kwargs)

    def safe(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return self(*args, **kwargs)
        except Exception as error:
            try:
                if self.handle:
                    return self.handle(error, *args, **kwargs)
            except Exception:
                self._handler_fail(error)

    def _handler_fail(self, error: Exception):
        logger.critical(f"{self} failed: {error}")

        match self.error_policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                logger.error(f"Original error: {error}")
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise

    @classmethod
    def from_func(
        cls,
        func: Callable[P, R],
        name: str,
        handle: Callable | None = None,
        error_policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE,
        exit_code: int = 1,
        emit: Callable | None = None,  # from Bus.Emitter
        **metadata: Any,
    ):
        return cls(
            func=func,
            name=name,
            handle=handle,
            error_policy=error_policy,
            exit_code=exit_code,
            emit=emit,
            **metadata,
        )


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Assembly
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@dataclass(kw_only=True)
class _TransferStrategy[**P, R](Functor[P, R]): ...
