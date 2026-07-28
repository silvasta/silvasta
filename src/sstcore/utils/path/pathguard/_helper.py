import functools
from pathlib import Path

from loguru import logger

from ....exceptions import (
    NotImplementedDispatchError,
    PathGuardError,
    PathGuardReason,
)
from ._input import PathInput, PathSpec


def relative_main(
    target: PathInput, root: PathInput | None = None, strict: bool = True
) -> Path:
    """Find Relative Path starting at Root (or CWD) downwards to Target"""

    _target = PathSpec.ok(target, resolve=True)
    _root = PathSpec.ok(root, resolve=True)

    if not strict:
        import os

        return Path(os.path.relpath(_target, _root))

    try:
        return _target.relative_to(_root)

    except ValueError as error:
        raise PathGuardError(
            PathGuardReason.RELATIVE, target=target, root=root, catched=error
        ) from error


def relative_string(source: Path, target: Path):  # TODO: PathInput?
    """Search relative Path in both direction and provide any rendering"""
    relative: Path | None = relative_duo(source, target)
    relative: Path = relative or relative_main(
        target=target, root=source, strict=False
    )
    return f"{source.name} -> {relative}"


def relative_duo(path1: PathInput, path2: PathInput) -> Path | None:
    """Search relative paths in both directions and provide Result or None"""

    _path1: Path = PathSpec.ok(path1)
    _path2: Path = PathSpec.ok(path2)

    try:
        rel21: Path | None = relative_main(_path1, _path2, strict=True)
    except PathGuardError:
        rel21: Path | None = None

    try:
        rel12: Path | None = relative_main(_path2, _path1, strict=True)
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
def split_read_print_path(target, local_root: Path | None = None):
    """
    Apply local_root or CWD at Target and create Path Pairs

    - 1 Absolute Path: computer readable safe for Operations
    - 1 Relative Path: human readable nice for Display

    """
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
            raise PathGuardError(
                PathGuardReason.RELATIVE,
                target=target,
                root=local_root,
                info="Missing local_root for relative Target",
            )
        read_path: Path = local_root / target
        print_path: Path = target

    return read_path, print_path
