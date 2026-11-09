"""
Calculate Relative Paths and produce renderable Strings

                         DependencyLevel.sstcore.util.path.guard[2]
"""

import os
from collections.abc import Iterable
from pathlib import Path
from typing import overload

from loguru import logger

from ....brick.call._argcast import castarg
from ....error import (
    NotImplementedDispatchError,
    PathGuardError,
    PathGuardReason,
)
from ._input import (
    MultiPath,
    PathArg,
    PathSpec,
    ResolvedPath,
    SinglePath,
    TargetPath,
    is_single_path,
)


@castarg
def _relative_one(
    target: ResolvedPath,
    /,
    root: ResolvedPath | None = None,
    *,
    strict: bool = True,
    must_exists: bool = False,
) -> Path:
    """
    Find Relative Path starting at Root (or CWD) downwards to Target

    - If not strict: walking as well upwards
    """
    # LATER: remove when replaced by castarg handling
    resolved_root: Path = root or Path.cwd().resolve()
    resolved_target: Path = _absolute_one(
        target, resolved_root, resolve=True, must_exists=must_exists
    )

    if not strict:
        return Path(os.path.relpath(resolved_target, resolved_root))
    try:
        return resolved_target.relative_to(resolved_root)
    except ValueError as error:
        raise PathGuardError(
            PathGuardReason.RELATIVE,
            target=resolved_target,
            root=resolved_root,
            caught=error,
        ) from error


@overload
def relative_main(
    target: SinglePath,
    /,
    root: PathArg | None = None,
    strict: bool = True,
    *,
    existing: bool = False,
) -> Path: ...


@overload
def relative_main(
    target: MultiPath,
    /,
    root: PathArg | None = None,
    strict: bool = True,
    *,
    existing: bool = False,
) -> list[Path]: ...


def relative_main(  # AI: this is mounted to PathGuard.relative
    target: SinglePath | MultiPath,
    /,
    root: PathArg | None = None,
    strict: bool = True,
    *,
    existing: bool = False,
) -> Path | list[Path]:
    """
    Find Relative Path(s) starting at Root (or CWD) downwards to Target(s).

    - Single PathArg -> Path
    - Iterable[PathArg] -> list[Path]
    - If not strict: walking upwards via '..' is permitted
    """
    resolved_root: Path = (
        PathSpec.ok(root, resolve=True)
        if root is not None
        else Path.cwd().resolve()
    )

    if is_single_path(target):
        return _relative_one(
            target,
            resolved_root,
            strict=strict,
            must_exists=existing,
        )

    if isinstance(target, Iterable):
        results: list[Path] = []
        for item in target:
            path: Path = _absolute_one(
                item,
                resolved_root,
                resolve=True,
                must_exists=False,
            )
            if not existing or path.exists():
                results.append(
                    _relative_one(path, resolved_root, strict=strict)
                )
        return results

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
    /,
    root: PathArg | None = None,
    *,
    resolve: bool = True,
    must_exists: bool = False,
) -> Path: ...


@overload
def absolute_main(
    target: MultiPath,
    /,
    root: PathArg | None = None,
    *,
    resolve: bool = True,
    must_exists: bool = False,
    filter_exists: bool = False,
) -> list[Path]: ...


def absolute_main(  # AI: this is mounted to PathGuard.absolute
    target: SinglePath | MultiPath,
    /,
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

    if is_single_path(target):
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


@castarg
def relative_string(source: TargetPath, target: TargetPath) -> str:
    """Search relative Path in both direction and provide any rendering"""
    relative: Path = relative_duo(source, target) or _relative_one(
        target, root=source, strict=False
    )
    return f"{source.name} -> {relative}"


@castarg
def relative_duo(path1: TargetPath, path2: TargetPath) -> Path | None:
    """Search relative paths in both directions and provide Result or None"""

    try:
        rel21: Path | None = _relative_one(path1, path2, strict=True)
    except PathGuardError:
        rel21 = None

    try:
        rel12: Path | None = _relative_one(path2, path1, strict=True)
    except PathGuardError:
        rel12 = None

    match (rel21, rel12):
        case (None, None):
            return None
        case (Path() as _p, None) | (None, Path() as _p):
            return _p
        case (Path() as _p1, Path() as _p2) if _p1 == _p2:
            return _p1

    logger.error(f"It happened! How is that possible??\n{rel21=}\n{rel12=}?")
    return None


def _split_one(
    target: PathArg, local_root: Path | None = None
) -> tuple[Path, Path]:
    root: Path = local_root or Path.cwd().resolve()
    read_path: Path = _absolute_one(target, root, resolve=False)
    print_path: Path = (
        read_path
        if local_root is None and read_path.is_absolute()
        else _relative_one(read_path, root, strict=False)
    )
    return read_path, print_path


@overload
def split(
    target: SinglePath,
    /,
    local_root: PathArg | None = None,
) -> tuple[Path, Path]: ...


@overload
def split(
    target: MultiPath,
    /,
    local_root: PathArg | None = None,
) -> list[tuple[Path, Path]]: ...


def split(
    target: SinglePath | MultiPath,
    /,
    local_root: PathArg | None = None,
) -> tuple[Path, Path] | list[tuple[Path, Path]]:
    """
    Apply local_root or CWD at Target and create Path Pairs:

    - 1 Absolute Path: computer readable safe for Operations
    - 1 Relative Path: human readable nice for Display
    """
    resolved_root: Path | None = (
        PathSpec.ok(local_root, resolve=True)
        if local_root is not None
        else None
    )

    if is_single_path(target):
        return _split_one(target, resolved_root)

    if isinstance(target, Iterable):
        return [_split_one(t, resolved_root) for t in target]

    raise NotImplementedDispatchError(target, local_root)
