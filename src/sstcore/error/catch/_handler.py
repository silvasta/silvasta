"""
Build the Functor for the Exception handling

                                                       DependencyLevel[0]
"""

from sstcore.port.functor import ErrorPolicy

from ...bricks.format import cls_name

__all__: list[str] = [
    "ErrorHandler",
]

import inspect
import sys
from collections.abc import Callable
from typing import NoReturn, Self

from ...bricks.func import SafeFunctor


class ErrorHandler[Error: BaseException](SafeFunctor[[Error], None]):
    """Handle CLI Exception and Terminate"""

    def __init__(self, exception_type: type[Error], **kwargs):
        self.exception_type: type[Error] = exception_type
        kwargs.setdefault("exit_code", 1)
        kwargs.setdefault("error_policy", ErrorPolicy.LOG_AND_EXIT)
        super().__init__(**kwargs)

    @property
    def _inside_brackets(self) -> str:
        return cls_name(target=self.exception_type)

    @classmethod
    def from_func(
        cls, func: Callable[[Error], None], exit_code: int = 1, name: str = ""
    ) -> Self:
        """Build with Exception type from signature"""

        sig: inspect.Signature = inspect.signature(func)
        first_param: inspect.Parameter = next(iter(sig.parameters.values()))
        inferred_type: type[Error] = first_param.annotation

        return cls(
            func=func,
            name=name or getattr(func, "__name__", "handler"),
            exception_type=inferred_type,
            exit_code=exit_code,
        )

    def execute_safe(self, error: Error) -> NoReturn:
        """Executes the handler, then terminates the CLI safely."""
        self.safe(error)
        sys.exit(self.exit_code)
