from importlib.metadata import PackageNotFoundError, version

from sstcore.utils.print import create_printer, printer

from .utils import PathGuard

try:  # show pyproject.toml package name
    __version__: str = version("sstcore")
except PackageNotFoundError:
    __version__ = "unknown"


__all__: list[str] = [
    "__version__",
    "PathGuard",
    "printer",
    "create_printer",
]

# TODO: quick improvements
# - ProjectFilter, default args -> config.json
# - FolderScanner, methods and args, summaryfile->targetenum
# - TreeSelector, remember past selection(s)

# TASK:
# - time management, UTC, maybe new lib
# - Exceptions, and how to link to SafeTyper
# - DiffFileManager, together with hardlink
