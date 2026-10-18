"""
Ensure Dir or File, exists or not

                         DependencyLevel.sstcore.util.path.guard[1]
"""

# IMPORTANT: Ensure in .__init__.pyi that PathArg is annotated for any Path

__all__: list[str] = [
    "_dir_logic",
    "dir",
    "_file_logic",  # LATER: dispatch: file_missing/exists
    "file",
    "_unique_candidate",
    "unique",
    "find_sequence",
]


import functools
import re
from collections.abc import Callable
from pathlib import Path

from loguru import logger

from ....error import PathGuardError, PathGuardReason
from ._arg import PathArg, PathSpec, TargetPath, castpath


@castpath
def _dir_logic(path: TargetPath, /) -> Path:
    """Ensure Directory is Writable"""
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


@castpath
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


def _unique_candidate(path: PathArg, ensure_parent: bool) -> Path:
    """PathGuard.unique implementation logic: Increment until Path is unique"""

    path: Path = PathSpec.ok(path)

    if not path.exists():
        msg = "path already unique, "
        if not path.parent.exists():
            if ensure_parent:  # TODO: as soon as this updated PathSpec
                _dir_logic(path.parent)
                logger.info(msg + "parent ensured!")
            else:
                logger.warning(f"{msg} take care before write! {path=}")

        return path

    # NOTE: Same logic as in find_sequence, consider when adapt!
    # AI_TASK: separate unique_sequence logic and provide _unique_candidate and find_sequence!
    original_stem: str = (  # prevent stuff like: my_archive.tar_1.gz
        path.name[: -len(suffixes)]  #
        if (suffixes := "".join(path.suffixes))
        else path.name
    )

    parent: Path = path.parent
    counter = 1

    while True:  # Safety loop to find free slot
        new_name = f"{original_stem}_{counter}{suffixes}"
        candidate: Path = parent / new_name
        if not candidate.exists():
            break
        counter += 1

    logger.info(f"Incremented: {candidate.name}")

    return candidate


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
        return _unique_candidate(target, ensure_parent)

    if callable(target):
        func: Callable[P, Path] = target

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
            path: Path = Path(func(*args, **kwargs))
            return _unique_candidate(path, ensure_parent)

        return wrapper

    if target is None:

        def decorator(func: Callable[P, Path]) -> Callable[P, Path]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path: Path = Path(func(*args, **kwargs))
                return _unique_candidate(path, ensure_parent)

            return wrapper

        return decorator

    raise PathGuardError(PathGuardReason.DECORATOR, target=target)


@castpath
def find_sequence(base_target: PathArg) -> list[Path]:
    """
    Find all Paths of a Sequence (base name + auto-incremented versions)

    Return list sorted by modification time (newest first)
    """

    # AI_TASK: separate unique_sequence logic and provide _unique_candidate and find_sequence!
    # TODO: sync with _operate.prune and with _unique_candidate

    base: Path = PathSpec.ok(base_target)

    if not (parent := base.parent).exists():
        return []

    # Same logic as in _unique_candidate, consider when adapt!
    suffixes: str = "".join(base.suffixes)
    original_stem: str = base.name[: -len(suffixes)] if suffixes else base.name

    #  re.escape to ensure special chars  don't break regex
    suffix_esc: str = re.escape(suffixes)
    stem_esc: str = re.escape(original_stem)

    # regex matches "stem.suffix" OR "stem_digits.suffix"
    pattern: re.Pattern[str] = re.compile(rf"^{stem_esc}(_\d+)?{suffix_esc}$")

    sequence: list[Path] = [
        item for item in parent.iterdir() if pattern.match(item.name)
    ]
    sequence.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return sequence
