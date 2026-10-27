"""
sstcore - Generalize Project Patterns and Bootstrap with Batteries

- System: Unite config, printer and bus and distribute
- Emitter: Launch events from ergonomic facade
- Printer: Visualize fast and with comfort
- ConfigManager: Bootstrap and simple access
- SafeTyper: CLI Pipeline with defaults
- PathGuard: Fail and File system safety


Top Level Packages:

- L6/󰉋 /console  # main interface and execution
- L5/󰉋 /data     # intermediate support layer
- L5/󰉋 /system   # command and control central
- L4/󰉋 /util     # structured helper and tools
- L3/󰉋 /error    # exceptions and handlers
- L2/󰉋 /forge    # shape compose and assemble
- L1/󰉋 /brick    # universal building blocks
- L0/󰉋 /port     # contracts and definitions


Rules:

Package and Subpackages are considered as one Module for Imports and Exports.

- From the outside perspective they share the same dependency level
- The Relative DependencyLevel starts internally again at 0
- Every import bumps the level to +1 of the level of the import
  - Consistently, the level of all export locations bumps as well
- The __init__ has always the highest level inside its package
  - its DependencyLevel[X] counts for the entire package like a module outside

Despite that dependency conflicts are already heavily relaxed due to the port:
  - Strict application is desired without any violation


Scratchpad and Experimental:

- '___{..}' Test/Idea/Todo Scratchpad: temporary storage with ruff verification
  - allowed in 'core' branch to collect history and ideas and outer branches
  - forbidden in 'main' branch

- '____{..}' Experimental or Out of Service: temporary storage
  - allowed in outer branches to keep ideas close or commit unsafe state
  - forbidden in 'core' and 'main' branch
"""

__all__: list[str] = [
    "System",
    "Emitter",
    "printer",
    "ConfigManager",
    "SafeTyper",
    "PathGuard",
    "portlink",
]

from .console import SafeTyper
from .port.link import portlink
from .system import System
from .system.config import ConfigManager
from .system.event import Emitter
from .util.path.guard import PathGuard
from .util.print import printer
