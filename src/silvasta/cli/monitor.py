import sys
import time
from pathlib import Path
from types import SimpleNamespace

from rich.console import Console
from rich.panel import Panel

from ..utils.parse import RegexMatch, LogPatterns
from ..utils.path import find_project_root, pyproject_log_section


def main(log_path: Path | None = None):
    """Show tail log display"""

    if log_path is None:
        root: Path = find_project_root("pyproject.toml")
        log_config: SimpleNamespace = pyproject_log_section()
        log_path: Path = root / "logs" / log_config.file_name

    console = Console()

    if not log_path.exists():
        if not log_path.parent.exists():
            # Avoid creating entire directories when the issue is most likely a wrong input path
            console.print(
                f"[bold red]Error:[/bold red] Log file {log_path} not found and no parent folder avaliable!"
            )
            sys.exit(1)

        log_path.touch()
        console.print(f"[dim]Created missing log file: {log_path}[/dim]")

    try:
        launch_tail_log_console(log_path)

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped tailing.[/yellow]")
        sys.exit(0)


def launch_tail_log_console(log_path: Path):
    """Launch console with live log prints from file assuming it is valid"""

    console = Console()
    console.print(
        Panel(  # TODO: move to printer, use Panel in default printer! title etc
            f"Tailing [bold cyan]{log_path}[/bold cyan] ...",
            title="Loguru Monitor",
        )
    )
    log_styles: dict[RegexMatch, str] = {
        LogPatterns.DEBUG: "bold yellow",
        LogPatterns.INFO: "bold white",
        LogPatterns.WARNING: "bold magenta",
        LogPatterns.ERROR: "bold red",
        LogPatterns.SUCCESS: "bold green",
    }
    with open(log_path, "r") as f:
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

            console.print(line.strip(), style=style)


if __name__ == "__main__":
    main()
