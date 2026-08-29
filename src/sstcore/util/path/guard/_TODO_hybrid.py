import functools
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ....error import PathGuardError, PathGuardReason
from ._input import PathSpec


def _as_path_input(target: object) -> bool:
    return isinstance(target, (Path, str, PathSpec))


def hybrid(logic: Logic, /) -> Callable[..., Any]:
    def main(target: object = None, **policy: Any) -> Any:
        if _as_path_input(target):
            return logic(target, **policy)
        if callable(target):
            fn = target

            @functools.wraps(fn)
            def wrapper(*args: Any, **kwargs: Any) -> Path:
                return logic(fn(*args, **kwargs), **policy)

            return wrapper
        if target is None:
            return lambda fn: main(fn, **policy)
        raise PathGuardError(PathGuardReason.DECORATOR, target=target)

    return main


dir = hybrid(_ensure_dir_logic)
file = hybrid(_ensure_file_logic)
unique_main = hybrid(_get_unique_candidate)
