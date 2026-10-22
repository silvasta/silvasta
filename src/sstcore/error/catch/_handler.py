"""
Build the Functor for the Exception handling

                             DependencyLevel.sstcore.error.catch[0]
"""

from sstcore.forge.engine import FunctorMetaData

__all__: list[str] = [
    "ErrorHandler",
]

import inspect
from collections.abc import Callable
from typing import Self

from ...brick.reflect import clsname
from ...forge.func import SafeFunctor
from ...port.functorial import ErrorPolicy


class ErrorHandler[Error: BaseException](
    SafeFunctor[[Error], None], data=FunctorMetaData()
):
    """Handle CLI Exception and Terminate"""

    def __init__(self, exception_type: type[Error], **kwargs):
        self.exception_type: type[Error] = exception_type
        kwargs.setdefault("exit_code", 1)
        kwargs.setdefault("error_policy", ErrorPolicy.LOG_AND_EXIT)
        super().__init__(name=clsname(self.exception_type), **kwargs)

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
