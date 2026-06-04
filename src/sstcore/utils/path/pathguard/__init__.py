from ._config import PathConfig, PathInput, _state
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
from ._operations import (
    SyncMode,
    copy,
    hardlink,
    prune,
    remove,
    rotate,
    symlink,
    trash,
)

__all__: list[str] = [
    "PathGuard",
    "PathConfig",
    "PathInput",
]


class PathGuard:
    """Centralized path enforcement toolkit"""

    SyncMode = SyncMode
    Config = PathConfig

    @staticmethod
    def debug(enable: bool):
        _state.debug = enable

    # --- Category 1: Structural Guards & Decorators ---
    dir = staticmethod(dir_main)
    file = staticmethod(file_main)
    unique = staticmethod(unique_main)
    find_sequence = staticmethod(find_sequence)

    # --- Category 2: Maintenance & Destruction Ops ---
    remove = staticmethod(remove)
    trash = staticmethod(trash)
    prune = staticmethod(prune)
    rotate = staticmethod(rotate)
    copy = staticmethod(copy)
    hardlink = staticmethod(hardlink)
    symlink = staticmethod(symlink)

    # --- Category 3: Evaluators & Diagnostics ---
    relative = staticmethod(relative_main)
    relative_duo = staticmethod(relative_duo)
    relative_string = staticmethod(relative_string)
    split_read_print_path = staticmethod(split_read_print_path)
