"""
Calculate Relative Paths and produce renderable Strings

                         DependencyLevel.sstcore.util.path.guard[2]
"""

import os
from collections.abc import Iterable
from pathlib import Path
from typing import overload

from loguru import logger

from ....error import (
    NotImplementedDispatchError,
    PathGuardError,
    PathGuardReason,
)
from ._arg import PathArg, PathSpec, ResolvedPath, castpath

type SinglePath = PathArg
type MultiPath = Iterable[PathArg]


@castpath
def _relative_one(
    target: ResolvedPath,
    root: ResolvedPath | None = None,
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


# AI: this is mounted to PathGuard.relative
# - before it handled only 1 Path at a time
def relative_main(
    target: SinglePath | MultiPath,
    root: PathArg | None = None,
    strict: bool = True,
) -> Path | list[Path]:
    """
    Find Relative Path(s) starting at Root (or CWD) downwards to Target(s).

    - Single PathArg -> Path
    - Iterable[PathArg] -> list[Path]
    - If not strict: walking upwards via '..' is permitted
    """
    if isinstance(target, (Path, str, PathSpec)):
        return _relative_one(target, root, strict=strict)  # ty:ignore FIX:

    if isinstance(target, Iterable):
        resolved_root: Path = (
            PathSpec.ok(root, resolve=True) if root is not None else Path.cwd()
        )
        return [
            _relative_one(item, resolved_root, strict=strict)  # ty:ignore FIX:
            for item in target
        ]

    raise NotImplementedDispatchError(target, root)


#  LINE: -- Absolut -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _absolute_one(
    target: PathArg,
    root: Path | None = None,
    *,
    resolve: bool = True,
    must_exists: bool = False,
) -> Path:
    raw_path: Path = PathSpec.normalize(target).target

    if not raw_path.is_absolute():
        if root is None:
            raise PathGuardError(
                PathGuardReason.RELATIVE,
                target=raw_path,
                root=root,
                info="Missing root for relative Target",
            )
        raw_path = root / raw_path

    return PathSpec.ok(raw_path, resolve=resolve, must_exists=must_exists)


@overload
def absolute_main(
    target: SinglePath,
    root: PathArg | None = None,
    *,
    resolve: bool = True,
    must_exists: bool = False,
) -> Path: ...


@overload
def absolute_main(
    target: MultiPath,
    root: PathArg | None = None,
    *,
    resolve: bool = True,
    must_exists: bool = False,
    filter_exists: bool = False,
) -> list[Path]: ...


def absolute_main(
    target: SinglePath | MultiPath,
    root: PathArg | None = None,
    *,
    resolve: bool = True,
    must_exists: bool = False,
    filter_exists: bool = False,
) -> Path | list[Path]:
    """
    Anchor relative Path(s) against `root` and validate via PathSpec.

    - Single PathArg -> Path
    - Iterable[PathArg] -> list[Path]
    - `must_exists=True`: raises PathGuardError if any target is missing
    - `filter_exists=True` (multi-mode): silently skips missing files
    """
    resolved_root: Path | None = (
        PathSpec.ok(root, resolve=True) if root is not None else None
    )

    if isinstance(target, (Path, str, PathSpec)):
        return _absolute_one(
            target, resolved_root, resolve=resolve, must_exists=must_exists
        )

    if isinstance(target, Iterable):
        results: list[Path] = []
        for item in target:
            path = _absolute_one(
                item,
                resolved_root,
                resolve=resolve,
                must_exists=must_exists and not filter_exists,
            )
            if not filter_exists or path.exists():
                results.append(path)
        return results

    raise NotImplementedDispatchError(target, root)


@castpath.duo  # CHECK: is this simply fix enough?
def relative_string(source: Path, target: Path):
    """Search relative Path in both direction and provide any rendering"""
    relative: Path = relative_duo(source, target) or _relative_one(
        target=target, root=source, strict=False
    )
    return f"{source.name} -> {relative}"


@castpath.duo  # CHECK: is this simply fix enough?
def relative_duo(path1: Path, path2: Path) -> Path | None:
    """Search relative paths in both directions and provide Result or None"""

    try:
        rel21: Path | None = _relative_one(path1, path2, strict=True)
    except PathGuardError:
        rel21: Path | None = None

    try:
        rel12: Path | None = _relative_one(path2, path1, strict=True)
    except PathGuardError:
        rel12: Path | None = None

    match (rel21, rel12):
        case (None, None):
            return None
        case (Path() as _p, None) | (None, Path() as _p):
            return _p

    logger.error(f"It happened! How is that possible??\n{rel21=}\n{rel12=}?")
    return None


@overload
def split(
    target: SinglePath, local_root: Path | None = None
) -> tuple[Path, Path]: ...


@overload
def split(
    target: MultiPath, local_root: Path | None = None
) -> list[tuple[Path, Path]]: ...


def split(
    target: SinglePath | MultiPath, local_root: Path | None = None
) -> tuple[Path, Path] | list[tuple[Path, Path]]:
    """
    Apply local_root or CWD at Target and create Path Pairs:

    - 1 Absolute Path: computer readable safe for Operations
    - 1 Relative Path: human readable nice for Display
    """
    if isinstance(target, (Path, str, PathSpec)):
        read_path = absolute_main(target, local_root, resolve=False)
        print_path = (
            read_path
            if local_root is None and read_path.is_absolute()
            else _relative_one(read_path, local_root)
        )
        return read_path, print_path

    if isinstance(target, Iterable):
        return [split(item, local_root) for item in target]

    raise NotImplementedDispatchError(target, local_root)
