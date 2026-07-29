"""
Build the Functor for the Exception handling

                                                       DependencyLevel[0]
"""

from ...format._normalize import cls_name

__all__: list[str] = [
    "ErrorHandler",
]

import inspect
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import NoReturn, Self

from loguru import logger


@dataclass(frozen=True)
class ErrorHandler[Error: BaseException]:
    """Handle CLI Exception and Terminate"""

    # IMPORTANT: chech if and how to attach Emitter func(box)
    name: str
    func: Callable[[Error], None]
    exception_type: type[Error]
    exit_code: int = 1

    @classmethod
    def from_func(
        cls, func: Callable, exit_code: int = 1, name: str | None = None
    ) -> Self:
        """Build with Exception type from signature"""

        sig: inspect.Signature = inspect.signature(func)
        first_param: inspect.Parameter = next(iter(sig.parameters.values()))
        inferred_type: type[Error] = first_param.annotation

        return cls(
            name=name or getattr(func, "__name__", "handler"),
            exception_type=inferred_type,
            func=func,
            exit_code=exit_code,
        )

    def execute_safe(self, error: Error) -> NoReturn:
        # IMPORTANT: inject emit:EmitFunc
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

    def __str__(self) -> str:
        return f"ErrorHandler[{cls_name(self.exception_type)}]"
