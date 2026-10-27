"""
Build the Error Handler Container

                             DependencyLevel.sstcore.error.catch[1]
"""

__all__: list[str] = [
    "ErrorRegistry",
]


from collections.abc import Callable
from typing import Any

from ...brick.reflect import objname
from ...brick.vault import DictVault
from ...port.link import portlink
from ...port.register import DictRegister, FuncRegister
from ._handler import DEFAULT_ERROR_HANDLER, ErrorHandler

type HandlerFunc[Error: Exception] = Callable[[Error], None]
type HandlerDecorator = Callable[[HandlerFunc], HandlerFunc]


@portlink(FuncRegister)
@portlink(DictRegister)
class ErrorRegistry(DictVault[ErrorHandler, type[BaseException]]):
    """
    Collect and Provide the ErrorHandler

    - Attach by function or Decorator
    - Access by Exception type as Key

    """

    def _item_id(self, item: ErrorHandler, /) -> type[Exception]:
        """Extract the exception class as the unique mapping key"""

        return item.error_type

    def _normalize(self, value: Any) -> ErrorHandler:
        """Ensure incoming items are valid ErrorHandler instances"""

        if isinstance(value, ErrorHandler):
            return value

        if callable(value) and not isinstance(value, type):
            return ErrorHandler.from_func(value)

        raise TypeError(
            f"Expected ErrorHandler or function, got {objname(value)}"
        )

    def _coerce_key(
        self, key: BaseException | type[BaseException]
    ) -> type[BaseException]:
        """Resolve Error to most specific registered MRO Key"""

        _error_type = key if isinstance(key, type) else type(key)

        for cls in _error_type.__mro__:
            if issubclass(cls, BaseException) and cls in self.vault:
                return cls

        return _error_type

    def use_default_shield(self) -> None:
        """Register fallback to Exception if not already present"""

        if Exception not in self.vault:
            self.add(DEFAULT_ERROR_HANDLER)

    def attach(self, exit_code: int = 2, name: str = "") -> HandlerDecorator:
        """Register Functions as ErrorHandler Functors"""

        def decorator[E: Exception](func: HandlerFunc[E]):
            handler: ErrorHandler[E] = ErrorHandler.from_func(
                func, exit_code=exit_code, name=name
            )
            self.add(handler)
            return func

        return decorator
