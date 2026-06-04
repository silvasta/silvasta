import functools
from pathlib import Path

from loguru import logger

from sstcore.exceptions import NotImplementedDispatchError

from ._ensure import _ensure_input

# TODO: better name than _helper?


def relative_string(source: Path, target: Path):
    relative: Path | None = relative_duo(source, target)
    relative: Path = relative or relative_main(
        target=target, root=source, strict=False
    )
    return f"{source.name} -> {relative}"


def relative_main(
    target: Path | str,
    root: Path | str | None = None,
    strict: bool = True,
    check_exists: bool = False,
    must_exists: bool = False,
) -> Path:
    """Find relative path starting at root|CWD downwards to target"""
    target_path: Path = _ensure_input(  # TASK: clean args
        path=target,
        resolve=True,
        check_exists=check_exists,
        must_exists=must_exists,
    )
    root_path: Path = _ensure_input(
        path=root or Path.cwd(),
        resolve=True,
        check_exists=check_exists,
        must_exists=must_exists,
    )
    if strict:
        try:
            return target_path.relative_to(root_path)
        except ValueError as e:
            msg = f"{target_path=} not found in {root_path=}"
            raise ValueError(msg) from e
    else:
        import os

        return Path(os.path.relpath(target_path, root_path))


def relative_duo(
    path1: Path | str,
    path2: Path | str,
    check_exists: bool = False,
    must_exists: bool = False,
) -> Path | None:
    """Find relative path from any of both directions or get None"""

    path1: Path = _ensure_input(  # TASK: args
        path=path1,
        check_exists=check_exists,
        must_exists=must_exists,
    )
    path2: Path = _ensure_input(
        path=path2,
        check_exists=check_exists,
        must_exists=must_exists,
    )
    try:
        rel21 = relative_main(path1, path2, strict=True)
    except ValueError:
        rel21 = None

    try:
        rel12 = relative_main(path2, path1, strict=True)
    except ValueError:
        rel12 = None

    match (rel21, rel12):
        case (None, None):
            logger.info("No relative path found in both directions...")
            return None

        case (Path() as _p, None) | (None, Path() as _p):
            logger.debug(f"found relative path: {_p}")
            return _p

        case _:
            logger.info("It happened, how is that possible?")
            logger.error(f"Found: {rel21} and {rel12}?")
            return None


@functools.singledispatch
def split_read_print_path(target, local_root: Path | None = None):
    raise NotImplementedDispatchError(target, local_root)


@split_read_print_path.register
def _(target: list, local_root: Path | None = None) -> list[tuple[Path, Path]]:
    return [split_read_print_path(path, local_root) for path in target]


@split_read_print_path.register
def _(target: Path, local_root: Path | None = None) -> tuple[Path, Path]:
    if target.is_absolute():
        read_path: Path = target
        print_path: Path = (
            target if local_root is None else relative_main(target, local_root)
        )
    else:  # Relative target
        if local_root is None:
            raise ValueError(
                f"Can't construct proper Path with {local_root=} for: {target=}"
            )
        read_path: Path = local_root / target
        print_path: Path = target
    return read_path, print_path
