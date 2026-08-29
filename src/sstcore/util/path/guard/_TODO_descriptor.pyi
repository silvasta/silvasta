from collections.abc import Callable
from pathlib import Path
from typing import Any, overload

class GuardedAttr:
    def __get__(self, obj: object, owner: type | None = None) -> Path: ...
    def __set__(self, obj: object, value: Path) -> None: ...
    def __call__(self, fget: Callable[[Any], Path]) -> GuardedAttr: ...

class PathGuard:
    @staticmethod
    def Dir(fget: Callable[[Any], Path]) -> GuardedAttr: ...
    @overload
    @staticmethod
    def File(fget: Callable[[Any], Path]) -> GuardedAttr: ...
    @overload
    @staticmethod
    def File(
        fget: None = None,
        *,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Callable[[Callable[[Any], Path]], GuardedAttr]: ...
    @staticmethod
    def Val(
        logic: Callable[..., Path],
        /,
        **policy: object,
    ) -> Callable[..., GuardedAttr]: ...
