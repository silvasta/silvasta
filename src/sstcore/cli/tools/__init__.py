"""
Provide tools standalone as Script or assemble to App

- folder_scanner: Attach FolderScanner and Treeselector to provide SummaryFile
- log_monitor: Read tail of log file and write updates in console

"""  # TODO: aktualisieren

from .app import app
from .monitor import log_monitor
from .scanner import folder_scanner

__all__: list = [
    "app",
    "folder_scanner",
    "log_monitor",
]
