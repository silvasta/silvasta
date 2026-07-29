"""
Build the Container for the Exception handling

                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "ErrorRegistry",
]

from collections.abc import Callable
from functools import singledispatchmethod

from .._general import NotImplementedDispatchError
from ._handler import ErrorHandler


class ErrorRegistry:
    """
    Collect and Provide the ErrorHandler

    - Attach 1 or multiple by function call or use Decorator
    - Store and provide access by Exception type as Key

    """

    # IMPORTANT: temporary registry for ErrorHandlerLoaders?
    # - collect them in advance but not already build
    # - build them when the Bus arrives

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
