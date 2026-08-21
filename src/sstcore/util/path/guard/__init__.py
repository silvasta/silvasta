"""Unite all Path Tools under PathGuard"""

__all__: list[str] = [
    "PathGuard",
    "PathSpec",
    "PathInput",
]

from collections.abc import Callable

from ....brick.meta import StaticToolkitMeta
from ....error import PathGuardReason
from . import _ensure, _input, _operate, _relative
from ._input import PathInput, PathSpec
from ._meta import PATH_GUARD_BOOT, _FormerPathGuardMeta


class TestPathGuard(metaclass=StaticToolkitMeta, data=PATH_GUARD_BOOT):
    """Safety and Comfort for Path access and File System operations"""

    # NOTE: type annotations and "docstrings" below are for DX

    """Category 1: Protect Path access operations to avoid File System fails"""
    dir: Callable = _ensure.dir
    file: Callable = _ensure.file
    unique: Callable = _ensure.unique_main
    find_sequence: Callable = _ensure.find_sequence

    """Category 2: Perform File Transfer operations with comfort and safety"""
    rotate: Callable = _operate.rotate
    copy: _operate.TransferStrategy = _operate.copy
    hardlink: Callable = _operate.hardlink
    symlink: Callable = _operate.symlink
    #
    remove: _operate.DeleteStrategy = _operate.remove
    trash: _operate.DeleteStrategy = _operate.trash
    prune: Callable = _operate.prune

    """Category 3: Use infrastructure for Relative Path and minor helpers.."""
    relative: Callable = _relative.relative_main
    relative_duo: Callable = _relative.relative_duo
    relative_string: Callable = _relative.relative_string
    split: Callable = _relative.split


class PathGuard(metaclass=_FormerPathGuardMeta):
    """Safety and Comfort for Path access and File System operations"""

    Spec: type[PathSpec] = _input.PathSpec
    SyncMode: type[SyncMode] = _operate.SyncMode
    Reason: type[PathGuardReason] = PathGuardReason

    """Category 1: Protect Path access operations to avoid File System fails"""
    dir = staticmethod(_ensure.dir)
    file = staticmethod(_ensure.file)
    unique = staticmethod(_ensure.unique_main)
    find_sequence = staticmethod(_ensure.find_sequence)

    """Category 2: Perform File Transfer operations with comfort and safety"""
    remove = staticmethod(_operate.remove)
    trash = staticmethod(_operate.trash)
    prune = staticmethod(_operate.prune)
    rotate = staticmethod(_operate.rotate)
    copy = staticmethod(_operate.copy)
    hardlink = staticmethod(_operate.hardlink)
    symlink = staticmethod(_operate.symlink)

    """Category 3: Use infrastructure for Relative Path and minor helpers.."""
    relative = staticmethod(_relative.relative_main)
    relative_duo = staticmethod(_relative.relative_duo)
    relative_string = staticmethod(_relative.relative_string)
    split = staticmethod(_relative.split)
