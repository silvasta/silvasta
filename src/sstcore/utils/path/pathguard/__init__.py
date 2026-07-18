"""Unite all Path Tools under PathGuard"""

__all__: list[str] = [
    "PathGuard",
    "PathArg",
    "PathInput",
]

from ._ensure import (
    dir_main,
    file_main,
    find_sequence,
    unique_main,
)
from ._helper import (
    relative_duo,
    relative_main,
    relative_string,
    split_read_print_path,
)
from ._input import PathArg, PathInput, _state
from ._operate import (
    SyncMode,
    copy,
    hardlink,
    prune,
    remove,
    rotate,
    symlink,
    trash,
)


class PathGuard:
    """
    Enable Safety and Comfort for Path access and File System operations

    - Demand level of input validation by PathInput and PathXXX
    """  # TODO: finish PathGuard doc

    # NEXT: format!

    SyncMode = SyncMode
    PathArg = PathArg

    @staticmethod
    def debug(enable: bool):
        _state.debug = enable

    """Category 1: Protect Path access operations to avoid File System fails"""
    dir = staticmethod(dir_main)
    file = staticmethod(file_main)
    unique = staticmethod(unique_main)
    find_sequence = staticmethod(find_sequence)

    """Category 2: Perform File Transfer operations with comfort and safety"""
    remove = staticmethod(remove)
    trash = staticmethod(trash)
    prune = staticmethod(prune)
    rotate = staticmethod(rotate)
    copy = staticmethod(copy)
    hardlink = staticmethod(hardlink)
    symlink = staticmethod(symlink)

    """Category 3: Use infrastructure for Relative Path and minor helpers.."""
    relative = staticmethod(relative_main)
    relative_duo = staticmethod(relative_duo)
    relative_string = staticmethod(relative_string)
    split_read_print_path = staticmethod(split_read_print_path)
