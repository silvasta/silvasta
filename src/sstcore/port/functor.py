from collections.abc import Callable
from enum import StrEnum
from typing import Any, Protocol


class ErrorPolicy(StrEnum):
    LOG_AND_CONTINUE = "log"
    LOG_AND_EXIT = "exit"
    RE_RAISE = "raise"


class Functorial[**P, R](Protocol):
    @property
    def name(self) -> str: ...
    @property
    def tags(self) -> set[str]: ...

    @classmethod
    def from_func(
        cls, func: Callable[P, R], name: str | None = None, **metadata: Any
    ) -> Functorial[P, R]: ...

    @property
    def error_policy(self) -> ErrorPolicy: ...
    @property
    def exit_code(self) -> int: ...

    # BOTH should enforce the signature
    def safe_call(self, *args: P.args, **kwargs: P.kwargs) -> R | None: ...
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    @property
    def func(self) -> Callable[P, R]: ...
    @property
    def metadata(self) -> dict[str, Any]: ...
