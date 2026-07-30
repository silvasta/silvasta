"""
sstcore  - Generalize frequent Patterns from Projects and Boot with Batteries included

- SafeTyper: CLI Pipeline with defaults
- ConfigManager: config bootstrap and access
- printer: nice prints and DX
- System: combined config, printer and bus
- PathGuard: file system safety

Dependency Level:
- Modules and packages start with DependencyLevel[0]
- Import from .local increases to DependencyLevel[level(.local) +1]
Strict application is desired without any violations.

"""

__all__: list[str] = [
    "__version__",
    "System",
    "EventBus",
    "ConfigManager",
    "printer",
    "SafeTyper",
    "PathGuard",
]

from importlib.metadata import PackageNotFoundError, version

from .cli import SafeTyper
from .config import ConfigManager
from .system import System
from .system.event import EventBus
from .utils.path import PathGuard
from .utils.print import printer

try:  # show pyproject.toml package name
    __version__: str = version("sstcore")
except PackageNotFoundError:
    __version__ = "unknown"
