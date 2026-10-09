"""
Temporary Storage for Protocols

- Move to sstcore.port when implementation successful

"""

import inspect
from typing import (
    Any,
    Protocol,
    runtime_checkable,
)


class ArgHandler[T](Protocol):
    def __call__(
        self,
        raw: Any,
        /,
        *,
        default: Any = inspect.Parameter.empty,
        name: str = "",
        param: inspect.Parameter | None = None,
    ) -> T: ...


@runtime_checkable
class Caster(Protocol):
    """Protocol for anything that can cast/validate an argument."""

    def __call__(
        self, value: Any, /, *, default: Any = inspect.Parameter.empty
    ) -> Any: ...
