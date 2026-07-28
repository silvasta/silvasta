"""Unite all Path Tools under PathGuard"""

from enum import StrEnum

__all__: list[str] = [
    "PathGuard",
]

from ....exceptions import PathGuardError, PathGuardReason
from . import _ensure, _helper, _input, _operate
from ._input import PathSpec
from ._meta import PathGuardMeta


class PathGuard(metaclass=PathGuardMeta):
    """
    Enable Safety and Comfort for Path access and File System operations

    - Use PathSpec for precise input control
    - ...

    """

    def __init__(self):
        """PathGuard is Not an Instance!"""
        raise PathGuardError(reason=PathGuardReason.NO_INSTANCE)

    Spec: type[PathSpec] = _input.PathSpec
    SyncMode: type[StrEnum] = _operate.SyncMode
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
    relative = staticmethod(_helper.relative_main)
    relative_duo = staticmethod(_helper.relative_duo)
    relative_string = staticmethod(_helper.relative_string)
    split_read_print_path = staticmethod(_helper.split_read_print_path)
