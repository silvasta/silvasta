"""
Build the Error Handler Container

                             DependencyLevel.sstcore.error.catch[1]
"""

__all__: list[str] = [
    "ErrorRegistry",
]

from collections.abc import Callable

from ...brick.vault import DictVault
from ...port.link import portlink
from ...port.register import DictRegister, FuncRegister
from ._handler import ErrorHandler

type HandlerFunc[Error: Exception] = Callable[[Error], None]
type HandlerDecorator = Callable[[HandlerFunc], HandlerFunc]


@portlink(FuncRegister)  # CHECK: is this proper??
@portlink(DictRegister)  # TASK: fix the mismatch of vault/proto
class ErrorRegistry(DictVault[ErrorHandler, type[Exception]]):
    """
    Collect and Provide the ErrorHandler

    - Attach by function or Decorator
    - Access by Exception type as Key

    """

    def _item_identifier(self, item: ErrorHandler):
        return item.exception_type, ErrorHandler

    def attach(self, exit_code: int = 2, name: str = "") -> HandlerDecorator:
        """Attach handler functions by decorator"""

        def decorator[E: Exception](func: HandlerFunc[E]):
            handler: ErrorHandler[E] = ErrorHandler.from_func(
                func, exit_code, name
            )
            # NEXT: figure out how to assing the Handler
            self[handler.exception_type] = handler
            return func

        return decorator
