"""
Store the logic of the initial pathguard grow

- from func to deco to hybrid to just the hybrid logic

"""

import functools
from collections.abc import Callable
from pathlib import Path
from typing import Any

# REMOVE: dependency issues
from sstcore.error import PathGuardError, PathGuardReason
from sstcore.util.path.guard._input import PathSpec

type Logic = Callable[..., Path]


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
