"""
Provide Setup for quick access to advanced Typer features

- SafeTyper: Bootstrap Log and Config, Register Error- and EventHandler

- sargs: Provide generalized Typer Arguments and Options

tools: Combine following utils inside example app

- folder_scanner: Attach FolderScanner and Treeselector to provide SummaryFile
- log_monitor: Read tail of log file and write updates in console

"""

from . import args as sargs
from .engine import SafeTyper
from .handler import ErrorHandler, ErrorRegistry
from .tools import app as tools

__all__: list = [
    "SafeTyper",
    "ErrorHandler",
    "ErrorRegistry",
    "sargs",
    "tools",
]
