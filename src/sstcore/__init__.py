"""
sstcore - Generalize Project Patterns and Bootstrap with Batteries

- System: Unite config, printer and bus and distribute
- Emitter: Launch events from ergonomic facade
- Printer: Visualize fast and with comfort
- ConfigManager: Bootstrap and simple access
- SafeTyper: CLI Pipeline with defaults
- PathGuard: Fail and File system safety

The Top Level Packages:

- L5/󰉋 /console  # current main interface
- L4/󰉋 /data     # intermediate support layer
- L4/󰉋 /system   # central  of the sstcore
- L3/󰉋 /util     # well prepared helpers
- L2/󰉋 /error    # exception and handlers
- L1/󰉋 /brick    # universal building blocks
- L0/󰉋 /port     # contracts and definitions


Package and Subpackages are considered like one Module for Imports and Exports.

- From an outside perspective all of them have the same dependency level
- Internally everything starts again at 0, every import bumps to +1 from import
- The __init__ has always the highest level inside its package
  - its DependencyLevel[X] counts for the entire package like a module outside

Despite that the port heavily relaxed dependency conflicts:
  - Strict application is desired without any violation


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

from .console import SafeTyper
from .system import System
from .system.config import ConfigManager
from .system.event import Emitter
from .util.path.guard import PathGuard
from .util.print import printer

try:
    __version__: str = version(distribution_name="sstcore")
    # Show pyproject.toml package name
except PackageNotFoundError:
    __version__ = "unknown"
