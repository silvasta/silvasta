"""
sstcore — Generalize recurring patterns in projects.

- SafeTyper: CLI Pipeline with defaults
- ConfigManager: config bootstrap and access
- printer: nice prints and DX
- System: combined config, printer and bus
- PathGuard: file system safety
"""

__all__: list[str] = [
    "__version__",
    "SafeTyper",
    "ConfigManager",
    "printer",
    "System",
    "PathGuard",
]

from importlib.metadata import PackageNotFoundError, version

from .cli import SafeTyper
from .config import ConfigManager
from .system import System
from .utils.path import PathGuard
from .utils.print import printer

try:  # show pyproject.toml package name
    __version__: str = version("sstcore")
except PackageNotFoundError:
    __version__ = "unknown"
