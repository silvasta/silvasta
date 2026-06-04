import functools
from pathlib import Path

from loguru import logger

from ....exceptions import NotImplementedDispatchError
from ._config import PathConfig, PathInput
from ._ensure import _ensure_input


def relative_string(source: Path, target: Path):
    # TODO: PathInput
    relative: Path | None = relative_duo(source, target)
    relative: Path = relative or relative_main(
        target=target, root=source, strict=False
    )
    return f"{source.name} -> {relative}"


def relative_main(
    target: PathInput, root: PathInput | None = None, strict: bool = True
) -> Path:
    """Find relative path starting at root|CWD downwards to target"""

    _target = _ensure_input(PathConfig.from_path_input(target, resolve=True))
    _root = _ensure_input(PathConfig.from_path_input(root, resolve=True))

    if strict:
        try:
            return _target.relative_to(_root)
        except ValueError as e:
            msg = f"{_target=} not found in {_root=}"
            raise ValueError(msg) from e
    else:
        import os

        return Path(os.path.relpath(_target, _root))


def relative_duo(path1: PathInput, path2: PathInput) -> Path | None:
    """Find relative path from any of both directions or get None"""

    _path1: Path = _ensure_input(path1)
    _path2: Path = _ensure_input(path2)

    try:
        rel21 = relative_main(_path1, _path2, strict=True)
    except ValueError:
        rel21 = None

    try:
        rel12 = relative_main(_path2, _path1, strict=True)
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
    # TODO: PathInput
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
