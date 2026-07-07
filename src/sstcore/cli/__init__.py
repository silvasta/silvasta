"""
Provide Setup for quick access to advanced Typer features

- SafeTyper: Register ExceptionHandlers and bootstrap Typer with Log and Config

- sargs: Provide generalized Typer Arguments and Options

utils_app: Combine following utils inside example app

- folder_scanner: Attach FolderScanner and Treeselector to provide SummaryFile
- log_monitor: Read tail of log file and write updates in console

"""

# TASK: modify when log_monitor gets powerful at next update

from . import args as sargs
from .engine import SafeTyper
from .launch import utils_app
from .monitor import log_monitor
from .scanner import folder_scanner

__all__: list = [
    "SafeTyper",
    "sargs",
    "utils_app",
    "folder_scanner",
    "log_monitor",
]
