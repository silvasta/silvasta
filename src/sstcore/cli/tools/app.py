"""
Collect and assemble mini-tools for example app

- transform util functions to Typer executables with Arg handling
"""

from pathlib import Path

from typer import Context, Option

from ...config import ConfigManager, SstPaths
from ...contract.log import LogDTO
from ...system import System
from ...tui import TreeSelectorApp
from ...tui.log_monitor import LogMonitorApp
from ...utils.path import any_root
from ...utils.print import printer
from ...utils.scanner.summary_file import SummaryFileBox
from .. import args as sargs
from ..engine import SafeTyper
from .monitor import log_monitor
from .scanner import folder_scanner


def main() -> None:
    app()


app = SafeTyper(name="tools", help="Basic equipment for development")


@app.command("monitor")
def launch_log_monitor_2(
    ctx: Context,
    file: sargs.LogFile = None,
    tail: bool = Option(True, help="Keep watching the file for new entries"),
):
    """Log Console Monitor: Analyze log file entries!"""

    config: ConfigManager = ctx.obj["config"]
    log_file: Path = file or config.log_result.struct_log_file

    def render_adapter(dto: LogDTO):
        return printer.render(dto)  # LATER: improve adapter

    app = LogMonitorApp(log_file, render_func=render_adapter, tail=tail)
    app.run()


@app.command("monitor1")
def launch_log_monitor_1(file: sargs.LogFile = None):  # TODO: improveCLI hint
    """Log Console Scroll: Watch new log file entries!"""
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
    # - writes confgi to other project...
    paths: SstPaths = system.config.paths
    if output_file is None:
        output_file: Path = paths.summary_file(suffix=file_type)
    scan_root: Path = scan_root or any_root()
    cache_file: Path = paths.scanner_cache_file(scan_root)
    folder_scanner(scan_root, output_file, cache_file, reset, sort, printer)


@app.command("config")
def config_details_and_write(ctx: Context, write_config: sargs.Write = False):
    """Print config to Console, optional write new json settings"""
    config: ConfigManager = ctx.obj["config"]
    printer(config)
    printer(config.settings)
    printer(config.setting_file)

    if write_config:
        config.save_settings()


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
