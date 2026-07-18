import inspect
import sys
from collections.abc import Callable
from dataclasses import dataclass
from functools import singledispatchmethod
from typing import NoReturn, Self

from loguru import logger

from ..exceptions import NotImplementedDispatchError

# TASK: default registry with some SstError implementations?


@dataclass(frozen=True)
class ErrorHandler[E: BaseException]:
    """Functor: Handle CLI Exception and Terminate"""

    name: str  # LATER: think about how to generalize
    func: Callable[[E], None]
    exception_type: type[E]
    exit_code: int = 1

    @classmethod
    def from_func(
        cls, func: Callable, exit_code: int = 1, name: str | None = None
    ) -> Self:
        """Build with Exception type from signature"""

        sig: inspect.Signature = inspect.signature(func)
        first_param: inspect.Parameter = next(iter(sig.parameters.values()))
        inferred_type: type[E] = first_param.annotation

        return cls(
            name=name or getattr(func, "__name__", "handler"),
            exception_type=inferred_type,
            func=func,
            exit_code=exit_code,
        )

    def __str__(self) -> str:
        return f"ErrorHandler[{self.exception_type.__name__}]"

    # LATER: think about how and if using: __call__

    def execute_safe(self, error: E) -> NoReturn:
        """Executes the handler, then terminates the CLI safely."""
        try:
            self.func(error)
            sys.exit(self.exit_code)  # Centralized exit!

        except SystemExit:
            raise  # Respect if the raw function explicitly calls sys.exit()

        except Exception as handler_fail:
            logger.critical(f"{self} failed during formatting: {handler_fail}")
            logger.error(f"Initial Error was: {error}")
            sys.exit(2)


class ErrorRegistry:
    """A staging area for error handlers before the CLI boots."""

    def __init__(self):
        self._registry: dict[type[BaseException], ErrorHandler] = {}

    @property
    def all(self) -> list[type[BaseException]]:
        """Provide list with all Exception types of all attached Handler"""
        return list(self._registry.keys())

    @property
    def n_handler(self) -> int:
        return len(self._registry)

    @singledispatchmethod
    def attach(self, handler: ErrorHandler | list[ErrorHandler]) -> None:
        """Add 1 or multiple handler to registry"""
        raise NotImplementedDispatchError(handler)

    @attach.register
    def _(self, handler: ErrorHandler) -> None:
        self._registry[handler.exception_type] = handler

    @attach.register
    def _(self, handler: list) -> None:
        for h in handler:
            self.attach(h)

    def get(self, exception_type: type[BaseException]) -> ErrorHandler | None:
        """Find handler for the exact exception"""
        return self._registry.get(exception_type)

    def handle(self, exit_code: int = 1, name: str | None = None):
        def decorator(func: Callable):
            self.attach(ErrorHandler.from_func(func, exit_code, name))
            return func

        return decorator
