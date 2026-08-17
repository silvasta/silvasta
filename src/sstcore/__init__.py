"""
sstcore - Generalize Project Patterns and Bootstrap with Batteries

- System: Unite config, printer and bus and distribute
- Emitter: Launch events from ergonomic facade
- Printer: Visualize fast and with comfort
- ConfigManager: Bootstrap config with simple access
- SafeTyper: CLI Pipeline with defaults
- PathGuard: Fail and File system safety

The Top Level Packages:

- L8/󰉋 /cli     # main execution of current tasks
- L7/󰉋 /tui     # cli boost and mini apps
- L6/󰉋 /data    # bridge raw/usage data and track
- L5/󰉋 /system  # core of the sstcore
- L4/󰉋 /config  # bridge online/offline config and compose
- L3/󰉋 /utils   # well prepared general helpers
- L2/󰉋 /error   # exceptions and handler with registry
- L1/󰉋 /bricks  # leaf like building blocks
- L0/󰉋 /port    # contracts for all essential objects


Package and Subpackages are considered like one Module for Imports and Exports.

Therefore the DependencyLevel[X]:
- Modules and Packages start with DependencyLevel[0]
- The __init__ has always the highest level inside its package
  - its DependencyLevel[X] counts for the outer package (like a module there)
- Imports from .some increase that to DependencyLevel[level_of(.some) +1]
  - this results in a bump of all upper modules in a counter chain

Strict application is desired without any violations.

"""

# AI_QUESTION: the current .cli import with SafeTyper could already causes issues,
# it triggers like other imports that might not be needed or installed, like:
# [project.optional-dependencies]
# cli = ["typer", "textual"]
# all = ["sstcore-py[cli]"]
# - where typer and textual should be explicitely optional

__all__: list[str] = [
    "__version__",
    "System",
    "Emitter",
    "printer",
    "ConfigManager",
    "SafeTyper",
    "PathGuard",
    # IDEAS: for top level __init__
    # - ColorBox? first finish the advanced apadter
    # - FileRegistry? but then File is needed as well...
    # - the port? as entire exported package?
    #   from sstcore import port
    #   ... port.config.Paths ...
    #   ... port.event.Event ...
    #   - unsure...
]

from importlib.metadata import PackageNotFoundError, version

from .cli import SafeTyper
from .config import ConfigManager
from .system import System
from .system.event import Emitter
from .utils.path.guard import PathGuard
from .utils.print import printer

try:
    # Show pyproject.toml package name
    __version__: str = version(distribution_name="sstcore")
except PackageNotFoundError:
    __version__ = "unknown"
