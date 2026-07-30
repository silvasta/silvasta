"""
Provide Setup for quick access to advanced Typer features

- SafeTyper: Bootstrap Log and Config, Register Error- and EventHandler

- sargs: Provide generalized Typer Arguments and Options

tools: Combine following utils inside example app

- folder_scanner: Attach FolderScanner and Treeselector to provide SummaryFile
- log_monitor: Read tail of log file and write updates in console

"""

from . import _args as sargs
from ._engine import SafeTyper
from ._tools import app as tools

__all__: list = [
    "sargs",
    "SafeTyper",
    "tools",
]
