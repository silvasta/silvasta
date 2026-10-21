"""
Calculate Relative Paths and produce renderable Strings

                         DependencyLevel.sstcore.util.path.guard[2]
"""

import functools
import os
from pathlib import Path

from loguru import logger

from ....error import (
    NotImplementedDispatchError,
    PathGuardError,
    PathGuardReason,
)
from ._arg import PathArg, ResolvedPath, castpath


@castpath
def relative_main(
    target: ResolvedPath,
    root: ResolvedPath | None = None,  # FIX: castpath->CWD!!
    strict: bool = True,
) -> Path:
    """
    Find Relative Path starting at Root (or CWD) downwards to Target

    - If not strict: walking as well upwards
    """
    root: Path = root or Path.cwd()

    if not strict:
        return Path(os.path.relpath(target, root))
    try:
        return target.relative_to(root)
    except ValueError as error:
        raise PathGuardError(
            PathGuardReason.RELATIVE, target=target, root=root, caught=error
        ) from error


def relative_string(source: Path, target: Path):  # TODO: PathArg?
    """Search relative Path in both direction and provide any rendering"""
    relative: Path = relative_duo(source, target) or relative_main(
        target=target, root=source, strict=False
    )
    return f"{source.name} -> {relative}"


@castpath
def relative_duo(path1: PathArg, path2: PathArg) -> Path | None:
    """Search relative paths in both directions and provide Result or None"""

    try:
        rel21: Path | None = relative_main(path1, path2, strict=True)
    except PathGuardError:
        rel21: Path | None = None

    try:
        rel12: Path | None = relative_main(path2, path1, strict=True)
    except PathGuardError:
        rel12: Path | None = None

    match (rel21, rel12):
        case (None, None):
            return None
        case (Path() as _p, None) | (None, Path() as _p):
            return _p

    logger.error(f"It happened! How is that possible??\n{rel21=}\n{rel12=}?")
    return None


@functools.singledispatch
def split(target, local_root: Path | None = None):
    """
    Apply local_root or CWD at Target and create Path Pairs

    - 1 Absolute Path: computer readable safe for Operations
    - 1 Relative Path: human readable nice for Display

    """
    raise NotImplementedDispatchError(target, local_root)


@split.register
def _(target: list, local_root: Path | None = None) -> list[tuple[Path, Path]]:
    # TASK: filter for existing return paths
    return [split(path, local_root) for path in target]


@split.register
def _(target: Path, local_root: Path | None = None) -> tuple[Path, Path]:

    if target.is_absolute():
        read_path: Path = target
        print_path: Path = (
            target if local_root is None else relative_main(target, local_root)
        )

    else:  # Relative target
        if local_root is None:
            raise PathGuardError(
                PathGuardReason.RELATIVE,
                target=target,
                root=local_root,
                info="Missing local_root for relative Target",
            )
        read_path: Path = local_root / target
        print_path: Path = target

    return read_path, print_path
