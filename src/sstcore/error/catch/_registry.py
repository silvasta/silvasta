"""
Build the Error Handler Container

                                                       DependencyLevel[1]
"""

from typing import TYPE_CHECKING

__all__: list[str] = [
    "ErrorRegistry",
]

from collections.abc import Callable

from ...brick.registry import DictRegistry
from ...port.registry import DictingRegistry, FunctionalRegistry
from ._handler import ErrorHandler  # REMOVE: proto???

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
        # FIX:
        return item.exception_type, ErrorHandler

    def attach(self, exit_code: int = 2, name: str = "") -> HandlerDecorator:
        """Attach handler functions by decorator"""

        def decorator(func: HandlerFunc):
            self.add(ErrorHandler.from_func(func, exit_code, name))
            return func

        return decorator


if TYPE_CHECKING:
    # LATER: implement and use FunctionalRegistry
    _instance_check: FunctionalRegistry = ErrorRegistry()
    _class_check: type[FunctionalRegistry] = ErrorRegistry
    #
    _instance_check: DictingRegistry = ErrorRegistry()
    _class_check: type[DictingRegistry] = ErrorRegistry
