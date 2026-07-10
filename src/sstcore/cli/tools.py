"""
Collect and assemble mini-tools for example app

- transform util functions to Typer executables with Arg handling
"""

from pathlib import Path

from typer import Context

from ..config import ConfigManager
from ..events import EventBus
from ..tui import TreeSelectorApp
from ..utils.print import printer
from . import args as sargs
from .engine import SafeTyper
from .monitor import log_monitor
from .scanner import folder_scanner


def main() -> None:
    app()


app = SafeTyper(name="tools", help="Basic equipment for development")


@app.command()
def empty(ctx: Context):
    """Launch default setup without any other exectution"""
    bus: EventBus = ctx.obj["bus"]
    printer("Start of 'empty' function...")
    printer.danger("END")
    bus.emit(event_name="ui.panel", sender="empty", payload=ctx)
    printer.success("End")


@app.command("monitor")
def launch_monitor(file: sargs.File = None):  # TODO: improveCLI hint
    """Log Console Monitor: Watch new log file entries!"""
    log_monitor(log_path=file)


@app.command("scanner")
def launch_folder_scanner(
    ctx: Context,
    scan_root: sargs.Root = None,
    output_file: sargs.File = None,
    # TODO: flag for reload, no cach
    sort: TreeSelectorApp.Sort = TreeSelectorApp.Sort.BY_SELECTION,
):
    """Folder Scanner with TreeSelector: Write combined file!"""
    # FIX: default args somehow corrupted...
    # - as well default filters, they work but fileter sometimes not as desired
    # -> must be usable at any file system location
    _config: ConfigManager = ctx.obj["config"]  # TODO: take paths
    folder_scanner(scan_root, output_file, sort_method=sort)


@app.command("print")
def print_file(path: Path):
    """Print Prompt, Response or any Markdown File in Rich style"""
    printer.title(path.name)
    match path.suffix:
        case ".json":
            printer(path.read_text())
        case ".md":
            printer.md(path.read_text())
        case _:  # LATER: other file types? match as function of printer?!
            printer.md(path.read_text())


if __name__ == "__main__":
    main()
