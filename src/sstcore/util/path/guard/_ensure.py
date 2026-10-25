"""
Ensure Dir or File, exists or not

                         DependencyLevel.sstcore.util.path.guard[1]
"""

# IMPORTANT: Ensure in .__init__.pyi that PathArg is annotated for any Path

from typing import TYPE_CHECKING

__all__: list[str] = [
    "_dir_logic",
    "dir",
    "_file_logic",  # LATER: dispatch: file_missing/exists
    "file",
    "unique",
]


import functools
from collections.abc import Callable
from pathlib import Path

from ....error import PathGuardError, PathGuardReason
from . import _increment
from ._arg import PathArg, PathSpec, TargetPath, castpath


@castpath.uno
def _dir_logic(path: TargetPath, /) -> Path:
    """Ensure Directory is Writable"""
    # reveal_type(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def dir[**P](
    target: Callable[P, Path] | PathArg,
) -> Callable[P, Path] | Path:
    """Hybrid: Ensure path is directory and exists, create if missing"""

    if isinstance(target, (Path, str, PathSpec)):
        return _dir_logic(target)

    if callable(target):
        func: Callable[P, Path] = target

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
            path: Path = func(*args, **kwargs)
            return _dir_logic(path)

        return wrapper

    raise PathGuardError(PathGuardReason.DECORATOR, target=target)


@castpath.uno_plus
def _file_logic(
    path: TargetPath, /, raise_error: bool, default_content: str | None
) -> Path:
    """Ensure File is Writable - no existing file at path!"""

    if path.exists():
        return path

    if default_content is not None:
        _dir_logic(path.parent)
        path.write_text(default_content)
        if not raise_error:
            return path
        info = f"Default File created: {path=}"
    else:
        info: str = (
            "Suppress Error works only when writing default_content!"
            if not raise_error
            else "execute regular raise"
        )

    raise PathGuardError(PathGuardReason.MISSING, target=path, info=info)


if TYPE_CHECKING:
    _file_logic("path", raise_error=False)  # ty:ignore FIX: missing default_content??
    _file_logic("path", raise_error=False, default_content="")


def file[**P](
    target: Callable[P, Path] | PathArg | None = None,
    *,
    raise_error=True,
    default_content: str | None = None,
) -> (
    Path
    | Callable[P, Path]
    | Callable[
        [Callable[P, Path]],
        Callable[P, Path],
    ]
):
    """Ensure path is file or write default content and | or Raise"""

    if isinstance(target, (Path, str, PathSpec)):
        return _file_logic(target, raise_error, default_content)

    if callable(target):
        func: Callable[P, Path] = target

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
            path = Path(func(*args, **kwargs))
            return _file_logic(path, raise_error, default_content)

        return wrapper

    if target is None:

        def decorator(func: Callable[P, Path]) -> Callable[P, Path]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path = Path(func(*args, **kwargs))
                return _file_logic(path, raise_error, default_content)

            return wrapper

        return decorator

    raise PathGuardError(PathGuardReason.DECORATOR, target=target)


def unique[**P](
    target: Callable[P, Path] | PathArg | None = None,
    ensure_parent=False,
) -> (
    Path
    | Callable[P, Path]
    | Callable[
        [Callable[P, Path]],
        Callable[P, Path],
    ]
):
    """
    Hybrid: Ensure Path does NOT exist.

    Apply auto-increments before suffix (file_1.txt, file_2.txt)

    - ensure_parent: create folder to ensure Path is writable
    """

    if isinstance(target, (Path, str, PathSpec)):
        return _increment.unique_candidate(target, ensure_parent)

    if callable(target):
        func: Callable[P, Path] = target

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
            path: Path = Path(func(*args, **kwargs))
            return _increment.unique_candidate(
                path, ensure_parent=ensure_parent
            )

        return wrapper

    if target is None:

        def decorator(func: Callable[P, Path]) -> Callable[P, Path]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path: Path = Path(func(*args, **kwargs))
                return _increment.unique_candidate(path, ensure_parent)

            return wrapper

        return decorator

    raise PathGuardError(PathGuardReason.DECORATOR, target=target)
