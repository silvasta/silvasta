"""
sstcore  - Generalize frequent Patterns from Projects and Boot with Batteries included

- System: combined config, printer and bus
- Emitter: ergonomic facade for event dispatch
- printer: nice prints and DX
- ConfigManager: config bootstrap and access
- SafeTyper: CLI Pipeline with defaults
- PathGuard: file system safety

Dependency Level:
- Modules and Packages start with DependencyLevel[0]
- Imports from .local increases to DependencyLevel[level(.local) +1]

Strict application is desired without any violations.

"""

__all__: list[str] = [
    "__version__",
    "System",
    "Emitter",
    "printer",
    "ConfigManager",
    "SafeTyper",
    "PathGuard",
]

from importlib.metadata import PackageNotFoundError, version

from .cli import SafeTyper
from .config import ConfigManager
from .system import System
from .system.event import Emitter
from .utils.path import PathGuard
from .utils.print import printer

try:  # show pyproject.toml package name
    __version__: str = version("sstcore")
except PackageNotFoundError:
    __version__ = "unknown"
