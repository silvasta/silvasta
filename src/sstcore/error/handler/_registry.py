"""
Build the Container for the Exception handling

                                                       DependencyLevel[1]
"""

from typing import TYPE_CHECKING

__all__: list[str] = [
    "ErrorRegistry",
]

from collections.abc import Callable

from ...port.registry import DictingRegistry, FunctionalRegistry
from ...utils.registry import DictRegistry
from ._handler import ErrorHandler

type HandlerFunc = Callable[[BaseException], None]
type HandlerDecorator = Callable[[HandlerFunc], HandlerFunc]


class ErrorRegistry(DictRegistry[ErrorHandler, type[BaseException]]):
    """
    Collect and Provide the ErrorHandler

    - Attach by function or Decorator
    - Access by Exception type as Key

    """

    def __init__(self):
        self.items: dict[type[BaseException], ErrorHandler] = {}

    def _item_identifier(self, item: ErrorHandler):
        return item.exception_type, ErrorHandler

    def register(self, exit_code: int = 1, name: str = "") -> HandlerDecorator:
        """Attach handler functions by decorator"""

        def decorator(func: HandlerFunc):
            self.attach(ErrorHandler.from_func(func, exit_code, name))
            return func

        return decorator


if TYPE_CHECKING:
    _instance_check: FunctionalRegistry = ErrorRegistry()
    _class_check: type[FunctionalRegistry] = ErrorRegistry
    #
    _instance_check: DictingRegistry = ErrorRegistry()
    _class_check: type[DictingRegistry] = ErrorRegistry
