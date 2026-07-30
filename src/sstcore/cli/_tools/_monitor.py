"""
Read from end of logfile and Display new entries

- so far with slightly colored lines of regular .log

"""

import sys
from pathlib import Path

from ...config import sst_config
from ...utils import PathGuard, printer
from ...utils.color import colorize
from ...utils.parse import LogMatcher


def log_monitor(log_path: Path | None = None, sleep=0.1):
    """Show tail log display"""

    log_file: Path = PathGuard.file(
        target=log_path or sst_config().settings.log.log_file,
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
