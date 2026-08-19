"""
Read from end of logfile and Display new entries

- so far with slightly colored lines of regular .log

"""

import sys
from pathlib import Path

from ...brick.color import colorize
from ...system.globals import config
from ...util import PathGuard, printer
from ...util.parse import LogMatcher


def log_monitor(log_path: Path | None = None, sleep=0.1):
    """Show tail log display"""

    log_file: Path = PathGuard.file(
        target=log_path or config().settings.log.log_file,
        default_content="",
        raise_error=False,
    )
    printer.title(f"Tailing {colorize.path(log_file)} ...", "Loguru Monitor")
    try:
        for line, style in LogMatcher.tail(log_file, sleep=sleep):
            printer(line, style=style)

    except KeyboardInterrupt:
        printer.warn("Log file tailing stopped")
        sys.exit(0)


if __name__ == "__main__":
    log_monitor()
