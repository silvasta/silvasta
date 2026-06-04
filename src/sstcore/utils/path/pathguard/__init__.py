from collections.abc import Callable

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

# from loguru import logger
# logger.remove()  # NEXT: check how cli looks without that


class PathGuard:
    """Centralized path enforcement toolkit"""

    SyncMode = SyncMode
    Config = PathConfig

    @staticmethod
    def debug(enable: bool):
        _state.debug = enable

    # --- Category 1: Structural Guards & Decorators ---
    dir: Callable = staticmethod(dir_main)
    file: Callable = staticmethod(file_main)
    unique: Callable = staticmethod(unique_main)
    find_sequence: Callable = staticmethod(find_sequence)

    # --- Category 2: Maintenance & Destruction Ops ---
    remove: Callable = staticmethod(remove)
    trash: Callable = staticmethod(trash)
    prune: Callable = staticmethod(prune)
    rotate: Callable = staticmethod(rotate)
    copy: Callable = staticmethod(copy)
    hardlink: Callable = staticmethod(hardlink)
    symlink: Callable = staticmethod(symlink)

    # --- Category 3: Evaluators & Diagnostics ---
    relative: Callable = staticmethod(relative_main)
    relative_duo: Callable = staticmethod(relative_duo)
    relative_string: Callable = staticmethod(relative_string)
    split_read_print_path: Callable = staticmethod(split_read_print_path)


__all__: list[str] = ["PathGuard", "PathConfig", "PathInput"]
