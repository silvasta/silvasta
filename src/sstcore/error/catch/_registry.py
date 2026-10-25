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
from ._handler import ErrorHandler

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
            f"Expected ErrorHandler or handler function, got {objname(value)}"
        )

    def _resolve_mro(
        self, exc: BaseException | type[BaseException]
    ) -> tuple[type[Exception], ErrorHandler[Any]] | None:
        exc_type = exc if isinstance(exc, type) else type(exc)
        for cls in exc_type.__mro__:
            if issubclass(cls, Exception) and cls in self.vault:
                return cls, self.vault[cls]
        return None

    def _key_item(
        self,
        key: BaseException | type[BaseException],
    ) -> ErrorHandler:
        """Enable error_registry[exc] to resolve via MRO."""
        if hit := self._resolve_mro(key):
            return hit[1]
        raise KeyError(key)

    def _box_key(
        self, key: BaseException | type[BaseException]
    ) -> dict[type[BaseException], ErrorHandler]:
        """Enable error_registry.find(exc) and .count(exc) to resolve via MRO."""
        if hit := self._resolve_mro(key):
            return {hit[0]: hit[1]}
        return {}

    def attach(self, exit_code: int = 2, name: str = "") -> HandlerDecorator:
        """Attach handler functions by decorator"""

        def decorator[E: Exception](func: HandlerFunc[E]):
            handler: ErrorHandler[E] = ErrorHandler.from_func(
                func, exit_code=exit_code, name=name
            )
            self.add(handler)
            return func

        return decorator
