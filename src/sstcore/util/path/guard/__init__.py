"""Unite all Path Tools under PathGuard"""

__all__: list[str] = [
    "PathGuard",
    "PathSpec",
    "PathInput",
]

from collections.abc import Callable
from typing import TYPE_CHECKING

from ....brick.color.box import Colors
from ....brick.format import cls_name
from ....brick.meta import StaticFuncMeta, StaticFuncMetaData
from ....error import PathGuardError, PathGuardReason
from ....port.call import Functorial
from ....port.color import ColorBox
from ....port.files import SyncMode
from . import _ensure, _operate, _relative
from ._input import PathInput, PathSpec

colors: ColorBox = Colors()  # ty:ignore


PathGuardMetaInput = StaticFuncMetaData(
    name=lambda cls: f" {cls_name(target=cls)} ",
    rich=f"{colors.azure('Path')}{colors.teal('Guard')}",
    # LATER: split by CamelCase (and then colorize)
    cli="Safety and Comfort for Path and File System operations",
    color=2,  # colors, names and even Enums change, but the registry index?
)

example = PathGuardError(PathGuardReason.NO_INIT)


class PathGuard(metaclass=StaticFuncMeta, data=PathGuardMetaInput):
    """Safety and Comfort for Path access and File System operations"""

    Spec: type[PathSpec] = PathSpec
    SyncMode: type[SyncMode] = SyncMode
    Reason: type[PathGuardReason] = PathGuardReason

    # AI: this was before the Meta upgrade:
    # def __init__(self):
    #     """PathGuard is Not an Instance!"""
    #     raise PathGuardError(reason=PathGuardReason.NO_INIT)

    ...

    # AI: the below docstring (imitations) and type hints are DX essentials
    # - the .pyi defines the public interface, this is for internal use

    """Category 1: Protect Path access operations to avoid File System fails"""

    dir: Callable = _ensure.dir
    file: Callable = _ensure.file
    unique: Callable = _ensure.unique_main
    find_sequence: Callable = _ensure.find_sequence

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


if TYPE_CHECKING:  # REMOVE: after tests
    _instance: Functorial = _operate.Rotate
    _instance: _operate.TransferStrategy = _operate.Hardlink
    _instance: Functorial = _operate.Remove
    _instance: _operate.DeleteStrategy = _operate.Trash
