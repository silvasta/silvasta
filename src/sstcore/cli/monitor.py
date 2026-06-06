import sys
import time
from pathlib import Path
from typing import Any

from ..config import get_config
from ..utils import PathGuard, printer
from ..utils.parse import LogPatterns


def log_monitor(log_path: Path | None = None):
    """Show tail log display"""
    log_file: Path = PathGuard.file(
        target=log_path or get_config().log_path,
        default_content="",
        raise_error=False,
    )
    try:
        launch_tail_log_console(log_file)

    except KeyboardInterrupt:
        printer.warn("Log file tailing stopped")
        sys.exit(0)


def launch_tail_log_console(log_file: Path):
    """Launch console with live log prints from file assuming it is valid"""
    cyan: Any = printer.colors.cyan

    printer.title(
        [f"Tailing {printer._format(log_file)} ..."],
        title=cyan("Loguru Monitor"),
        title_align="right",
        frame="purple",
    )

    with open(log_file) as f:
        f.seek(0, 2)  # Move to end of file

        while True:
            if not (line := f.readline()):
                time.sleep(0.1)
                continue

            match line:  # FIX: broken... since  when??
                case LogPatterns.DEBUG:
                    style: str = "bold yellow"
                case LogPatterns.INFO:
                    style: str = "bold white"
                case LogPatterns.WARNING:
                    style: str = "bold magenta"
                case LogPatterns.ERROR:
                    style: str = "bold red"
                case LogPatterns.SUCCESS:
                    style: str = "bold green"
                case _:
                    style = None

            printer(line.strip(), style=style)


if __name__ == "__main__":
    log_monitor()
