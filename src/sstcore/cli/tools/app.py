"""
Collect and assemble mini-tools for example app

- transform util functions to Typer executables with Arg handling
"""

from pathlib import Path

from loguru import logger
from typer import Context, Option

from ...config import SstPaths
from ...contract.cli import PanelDTO
from ...contract.log import LogDTO
from ...system import EventBus, System
from ...tui import TreeSelectorApp
from ...tui.log_monitor import LogMonitorApp
from ...utils.path import PathGuard, any_root
from ...utils.print import printer
from ...utils.scanner.summary_file import SummaryFileBox
from .. import args as sargs
from ..engine import SafeTyper
from .monitor import log_monitor
from .scanner import folder_scanner


def main() -> None:
    app()


app = SafeTyper(name="tools", help="Basic equipment for development")


@app.command()
def empty(ctx: Context):  # WARN: remove in sstcore/main
    """Launch default setup without any other execution"""
    bus: EventBus = ctx.obj["bus"]
    printer("Start of 'empty' function...")
    printer.danger("END")
    bus.emit(event_name="ui.panel", sender="empty", payload=ctx)
    logger.debug("hello")
    logger.success("it works")
    panel = PanelDTO(text="dto check")
    bus.emit(
        event_name="sys.log",
        sender="empty",
        payload=panel,
    )
    printer(panel)
    bus.emit(
        event_name="sys.log", sender="empty", payload={"a": 1, "b": Path()}
    )
    printer.success("End")


@app.command()
def monitor2(
    ctx: Context,
    file: sargs.LogFile = None,
    tail: bool = Option(True, help="Keep watching the file for new entries"),
):
    system: System = ctx.obj["system"]
    _log_file: Path = PathGuard.file(
        target=file or system.config.settings.log.log_file,
        default_content="",
        raise_error=False,
    )
    log_file = Path("/home/silvan/sstcore/logs/sstcore.jsonl")

    def render_adapter(dto: LogDTO):
        return printer.render(dto)  # NEXT: check adapter

    app = LogMonitorApp(log_file, render_func=render_adapter, tail=tail)
    app.run()


@app.command()
def monitor1(file: sargs.LogFile = None):  # TODO: improveCLI hint
    """Log Console Monitor: Watch new log file entries!"""
    # TASK: Log Monitor 2
    # - improve existing match and log tail
    # - extend log tail to ndjson, use LogDTO.level for match
    # - create LogDTO panel or other nice rich style print in printer
    # - simple scroll ndjson log
    # - simple TUI with scroll + dynamic filter change
    #   LATER:
    #   - usage for existing logs
    #   - usage with live bus connection
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
