"""
Assemble all Tools to PathGuard

                         DependencyLevel.sstcore.util.path.guard[4]
"""

from pathlib import Path

__all__: list[str] = [
    "PathGuard",
    "PathSpec",
    "PathArg",
]

from collections.abc import Callable

from ....brick.color.box import Colors
from ....brick.reflect import clsname
from ....error import PathGuardError, PathGuardReason
from ....forge.engine import StaticFuncMeta, StaticFuncMetaData
from ....port.files import SyncMode
from ....port.link import tap
from . import _ensure, _field, _increment, _lock, _operate, _relative
from ._arg import PathArg, PathSpec

colors = Colors()

PathGuardMetaInput = StaticFuncMetaData(
    name=lambda cls: f" {clsname(cls)} ",
    rich=f"{colors.azure('Path')}{colors.teal('Guard')}",
    cli="Safety and Comfort for Path and File System operations",
    # LATER: split by PascalCase (and then colorize)
    color=2,
)

_example = PathGuardError(PathGuardReason.NO_INIT)


class PathGuard(metaclass=StaticFuncMeta, data=PathGuardMetaInput):
    """Safety and Comfort for Path access and File System operations"""

    # NEXT: add PathCast

    Spec: type[PathSpec] = PathSpec
    SyncMode: type[SyncMode] = SyncMode
    Reason: type[PathGuardReason] = PathGuardReason

    # AI: the below docstring (imitations) and type hints are DX essential
    # - the .pyi defines the public interface, this is for internal use

    """Category 1: Protect Path access operations to avoid File System fails"""

    dir: Callable = _ensure.dir
    file: Callable = _ensure.file
    unique: Callable = _ensure.unique
    find_sequence: Callable = _increment.find_sequence

    Lock = _lock.Lock

    Dir = _field.DirField
    Fil = _field.FileField
    Unique = _field.UniqueField
    SpecField = _field.PathSpecField

    """Category 2: Perform File Transfer operations with comfort and safety"""

    TODO_TRANSFER_STRATEGY: _operate.TransferStrategy = _operate.Rotate
    rotate: Callable = _operate.rotate
    copy: Callable = _operate.copy
    hardlink: Callable = _operate.hardlink
    symlink: Callable = _operate.symlink

    TODO_DELETE_STRATEGY: _operate.DeleteStrategy = _operate.Trash
    remove: Callable = _operate.remove
    trash: Callable = _operate.trash
    prune: Callable = _operate.prune

    """Category 3: Use infrastructure for Relative Path and minor helpers.."""

    relative: Callable = _relative.relative_main
    relative_duo: Callable = _relative.relative_duo
    relative_string: Callable = _relative.relative_string
    split: Callable = _relative.split


if __name__ == "__main__":
    # from typing import reveal_type
    # from rich import print
    #  LINE: -- Examples -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    @PathGuard.dir
    def _my_dir() -> Path:
        result = Path.cwd() / "experiments"
        # reveal_type(result)
        return result

    @PathGuard.file(default_content="", raise_error=False)
    def _my_file() -> Path:
        result = _my_dir() / "my_file.md"
        # reveal_type(result)
        return result

    @PathGuard.unique
    def _my_unique() -> Path:
        result = _my_dir() / "my_file.md"
        # reveal_type(result)
        return result

    _unique = _my_unique()
    print(_unique)

    _relative = PathGuard.relative(_unique)
    print(_relative)

    PathGuard.remove(_my_file())

    tap.emit(PathGuard)

    # NOTE: use: export SST_DEBUG=__main__
    # (color still missing...)
    print(f"{tap.watches(PathGuard)=}")
    print(f"{tap.spec.channels=}")
    print(f"{tap.spec.channels.key(PathGuard)}")
