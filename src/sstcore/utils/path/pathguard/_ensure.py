import functools
import re
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, cast

from loguru import logger

from ._config import PathConfig, PathInput, _state

P = ParamSpec("P")  # REMOVE: after fixing types (Python 3.14)

# TASK: apply new PathInput


def _ensure_input(path_input: PathInput) -> Path:
    """Normalize strings, Paths, or PathConfig instances into validated Path objects."""

    if isinstance(path_input, PathConfig):
        path = Path(path_input.target)
        resolve: bool = path_input.resolve
        check_exists: bool = path_input.check_exists
        must_exists: bool = path_input.must_exists
    else:
        path = Path(path_input)
        resolve = check_exists = must_exists = False

    if resolve:
        path: Path = path.resolve()

    if check_exists or must_exists:
        text: str = "exists!" if path.exists() else "not found on disk!"
        msg = f"Input {text} for: {path=}"

        if check_exists:
            logger.info(msg)
        if must_exists:
            if not path.exists():
                raise FileNotFoundError(msg)

            if _state.debug:
                logger.debug(msg)

    return path


def _ensure_dir_logic(path: Path | str) -> Path:
    """The actual implementation logic"""
    path: Path = _ensure_input(path)
    path.mkdir(parents=True, exist_ok=True)
    if _state.debug:
        logger.debug(f"directory ensured: {path}")
    return path


# FIX: ParamSpec
def dir_main(
    target: Callable[P, Path] | Path | str,
) -> Callable[P, Path] | Path:
    """Hybrid: Ensure path is directory and exists, create if missing"""

    # Case 1: Used as a Function Call (PathGuard.dir(path))
    if isinstance(target, (Path, str)):
        return _ensure_dir_logic(target)

    # Case 2: Used as a Decorator (@PathGuard.dir)
    if callable(target):
        func = cast(Callable[P, Path], target)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
            path: Path = func(*args, **kwargs)
            return _ensure_dir_logic(path)

        return wrapper

    raise TypeError(f"Invalid target type for PathGuard.dir: {type(target)}")


def _ensure_file_logic(
    path: Path | str, raise_error: bool, default_content: str | None
) -> Path:

    path: Path = _ensure_input(path)

    if path.exists():
        return path

    logger.warning(f"No file found at: {path}")

    if default_content is not None:  # write first
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(default_content)
        logger.info(f"Created default file: {path=}")

        if raise_error:
            msg = f"Critical file created, modify at: {path=}"
        else:
            return path
    else:
        if raise_error:
            msg = f"Critical file missing: {path=}"
        else:
            warn = "Suppress error only allowed for case of writing file with default content!"
            logger.warning(warn)
            msg = f"Wrong input, file not confirmed: {path=}"

    raise FileNotFoundError(msg)


# FIX: ParamSpec
def file_main(
    target: Callable[P, Path] | Path | str | None = None,
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
    """Ensure path is file, write default content and | or raise error"""

    # CASE 1: Function Call -> PathGuard.file(path)
    if isinstance(target, (Path, str)):
        return _ensure_file_logic(target, raise_error, default_content)

    # CASE 2: Bare Decorator -> @PathGuard.file
    if callable(target):
        func = cast(Callable[P, Path], target)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
            path = Path(func(*args, **kwargs))
            return _ensure_file_logic(path, raise_error, default_content)

        return wrapper

    # CASE 3: Decorator with Arguments -> @PathGuard.file(default_content="...")
    if target is None:

        def decorator(func: Callable[P, Path]) -> Callable[P, Path]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path = Path(func(*args, **kwargs))
                return _ensure_file_logic(path, raise_error, default_content)

            return wrapper

        return decorator


def _get_unique_candidate(path: Path | str, ensure_parent: bool) -> Path:
    """Internal logic: Appends counter until a free filename is found."""

    path: Path = _ensure_input(path)

    if not path.exists():
        msg = "path already unique, "
        if path.parent.exists():
            if _state.debug:
                logger.debug(msg + "path has parent")
        else:
            msg += "path has no parent, "
            if ensure_parent:
                _ensure_dir_logic(path.parent)
                logger.info(msg + "parent ensured!")
            else:
                logger.warning(f"{msg} take care before write! {path=}")

        return path

    # Same logic as in find_sequence, consider when adapt!
    suffixes: str = "".join(path.suffixes)
    original_stem: str = (  # prevent f.e. my_archive.tar_1.gz
        path.name[: -len(suffixes)] if suffixes else path.name
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


# FIX: ParamSpec
def unique_main(
    target: Callable[P, Path] | Path | str | None = None,
    ensure_parent=False,
) -> (
    Path
    | Callable[P, Path]
    | Callable[
        [Callable[P, Path]],
        Callable[P, Path],
    ]
):
    """Hybrid: Ensures the returned path does NOT exist,
    ensure_parent creates folder to make it directly writable.
    If it exists, auto-increments suffix (file_1.txt, file_2.txt)
    """

    # Case 1: Direct call (PathGuard.unique(path))
    if isinstance(target, (Path, str)):
        return _get_unique_candidate(target, ensure_parent)

    # Case 2: Bare Decorator (@PathGuard.unique)
    if callable(target):
        func = cast(Callable[P, Path], target)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
            path: Path = Path(func(*args, **kwargs))
            return _get_unique_candidate(path, ensure_parent)

        return wrapper

    # CASE 3: Decorator with args -> @PathGuard.unique(ensure_parent=True)
    if target is None:

        def decorator(func: Callable[P, Path]) -> Callable[P, Path]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path: Path = Path(func(*args, **kwargs))
                return _get_unique_candidate(path, ensure_parent)

            return wrapper

        return decorator


def find_sequence(base_target: Path | str) -> list[Path]:
    """Find all paths of a sequence (base name + auto-incremented versions)
    returns list, sorted by modification time (newest first)"""

    base: Path = _ensure_input(base_target)

    if not (parent := base.parent).exists():
        return []

    # Same logic as in _get_unique_candidate, consider when adapt!
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
