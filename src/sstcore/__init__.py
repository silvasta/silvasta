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

__all__: list[str] = [
    "__version__",
    "System",
    "Emitter",
    "printer",
    "ConfigManager",
    "SafeTyper",
    "PathGuard",
    # IDEA: "port", ???
]


from importlib.metadata import PackageNotFoundError, version

from .port.functional import python_is_latest

if python_is_latest():
    lazy from .cli import SafeTyper
    lazy from .config import ConfigManager
    lazy from .system import System
    lazy from .system.event import Emitter
    lazy from .utils.path.guard import PathGuard
    lazy from .utils.print import printer

else:

    def __getattr__(name: str):
        if name in (
            lazy_map := {
                "SafeTyper": ".cli",
                "ConfigManager": ".config",
                "System": ".system",
                "Emitter": ".system.event",
                "PathGuard": ".utils.path.guard",
                "printer": ".utils.print",
            }
        ):
            from importlib import import_module

            return getattr(import_module(lazy_map[name], __name__), name)
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    def __dir__() -> list[str]:
        return __all__


try:  # Show pyproject.toml package name
    __version__: str = version(distribution_name="sstcore")
except PackageNotFoundError:
    __version__ = "unknown"
