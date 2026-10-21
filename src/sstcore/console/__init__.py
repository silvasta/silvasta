"""
Provide Setup for quick access to advanced Terminal features

- SafeTyper: Bootstrap Log and Config, Register Error- and EventHandler

- sargs: Provide generalized Typer Arguments and Options
         (sargs because project already use args)

- tools: Assemble and Launch Utils
  - folder_scanner: FolderScanner -> Treeselector -> SummaryFile
  - log_monitor: LogFile / EventBus -> Interactive TUI

                                                       DependencyLevel[5]
"""

__all__: list = [
    "sargs",
    "SafeTyper",
]
from . import _args as sargs
from ._engine import SafeTyper
