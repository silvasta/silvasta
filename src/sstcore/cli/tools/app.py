"""
Collect and assemble mini-tools for example app

- transform util functions to Typer executables with Arg handling
"""

from pathlib import Path

from typer import Context

from sstcore.core import System
from sstcore.utils.path import any_root
from sstcore.utils.scanner.summary_file import SummaryFileBox

from ...config import SstPaths
from ...events import EventBus
from ...tui import TreeSelectorApp
from ...utils.print import printer
from .. import args as sargs
from ..engine import SafeTyper
from .monitor import log_monitor
from .scanner import folder_scanner


def main() -> None:
    app()


app = SafeTyper(name="tools", help="Basic equipment for development")


@app.command()
def empty(ctx: Context):  # WARN: remove in sstcore/main
    """Launch default setup without any other exectution"""
    bus: EventBus = ctx.obj["bus"]
    printer("Start of 'empty' function...")
    printer.danger("END")
    bus.emit(event_name="ui.panel", sender="empty", payload=ctx)
    printer.success("End")


@app.command("monitor")
def launch_monitor(file: sargs.LogFile = None):  # TODO: improveCLI hint
    """Log Console Monitor: Watch new log file entries!"""
    log_monitor(log_path=file)


@app.command("scanner")
def launch_folder_scanner(
    ctx: Context,
    scan_root: sargs.Root = None,
    output_file: sargs.OutputFile = None,
    file_type: SummaryFileBox = SummaryFileBox.MD,  # TODO: help text
    reset: sargs.CleanState = False,
    sort: TreeSelectorApp.Sort = TreeSelectorApp.Sort.SELECTION,
    # filter:FilterBox=FilterBox.EMPTY # TODO:
):
    """Folder Scanner with TreeSelector: Write combined file!"""
    system: System = ctx.obj["system"]
    # FIX: config.paths fails if executed outside the project,
    # anyway needed to change home setup (dynamically) when publishing
    paths: SstPaths = system.config.paths
    if output_file is None:
        output_file: Path = paths.summary_file(suffix=file_type)
    scan_root: Path = scan_root or any_root()
    cache_file: Path | None = (
        None if reset else paths.scanner_cache_file(scan_root)
    )
    folder_scanner(scan_root, output_file, cache_file, sort, printer)


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
