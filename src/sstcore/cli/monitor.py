import sys
import time
from pathlib import Path
from types import SimpleNamespace

from loguru import logger

from ..utils import PathGuard, printer
from ..utils.parse import LogPatterns, RegexMatch
from ..utils.path import find_project_root, pyproject_log_section


def main(log_path: Path | None = None):
    """Show tail log display"""

    if log_path is None:
        root: Path = find_project_root("pyproject.toml")
        log_config: SimpleNamespace = pyproject_log_section()
        log_path: Path = PathGuard.file(
            root / log_config.log_dir / log_config.file_name,
            raise_error=False,
        )

    if not log_path.exists():
        if not log_path.parent.exists():
            printer("no log path parent")
            # Avoid creating directories when the issue is most likely failed path
            logger.error(f"No file found at: {log_path=}")
            logger.info(
                "Parent folder not available -> no empty file created!"
            )

            sys.exit(1)

        log_path.touch()
        logger.warning(f"Created missing log file at: {log_path=}")

    try:
        launch_tail_log_console(log_path)

    except KeyboardInterrupt:
        printer.warn("Log file tailing stopped", style="yellow")
        sys.exit(0)


def launch_tail_log_console(log_path: Path):
    """Launch console with live log prints from file assuming it is valid"""

    printer.panel(
        f"Tailing [bold cyan]{log_path}[/bold cyan] ...",
        title="Loguru Monitor",
    )
    log_styles: dict[RegexMatch, str] = {
        LogPatterns.DEBUG: "bold yellow",
        LogPatterns.INFO: "bold white",
        LogPatterns.WARNING: "bold magenta",
        LogPatterns.ERROR: "bold red",
        LogPatterns.SUCCESS: "bold green",
    }
    with open(log_path) as f:
        f.seek(0, 2)  # Move to end of file

        while True:
            if not (line := f.readline()):
                time.sleep(0.1)  # save CPU
                continue

            match line:
                case (
                    LogPatterns.DEBUG
                    | LogPatterns.INFO
                    | LogPatterns.WARNING
                    | LogPatterns.ERROR
                    | LogPatterns.SUCCESS as matcher
                ):  # Coloring based on Loguru levels
                    style: str = log_styles[matcher]
                case _:
                    style = None

            printer(line.strip(), style=style)


if __name__ == "__main__":
    main()
