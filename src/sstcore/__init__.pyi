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
- L4/󰉋 /system   # central of the sstcore
- L3/󰉋 /util     # well organized helpers
- L2/󰉋 /error    # exception and handlers
- L1/󰉋 /brick    # universal building blocks
- L0/󰉋 /port     # contracts and definitions


Package and Subpackages are considered like one Module for Imports and Exports.

- From an outside perspective all of them have the same dependency level
- Internally everything starts again at 0, every import bumps to +1 from import
- The __init__ has always the highest level inside its package
  - its DependencyLevel[X] counts for the entire package like a module outside

Despite that dependency conflicts are heavily relaxed with the port:
  - Strict application is desired without any violation

"""

__all__: list[str] = [
    "System",
    "Emitter",
    "printer",
    "ConfigManager",
    "SafeTyper",
    "PathGuard",
]

from .console import SafeTyper
from .system import System
from .system.config import ConfigManager
from .system.event import Emitter
from .util.path.guard import PathGuard
from .util.print import printer
