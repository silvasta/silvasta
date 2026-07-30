"""
Collect and assemble mini-tools for example app

- transform util functions to Typer executables with Arg handling
"""

from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
from typer import Context, Option

from ...config import ConfigManager, SstPaths
from ...port import LogDTO
from ...system import System
from ...tui import LogMonitorApp
from ...tui.selector import TreeSelectorApp
from ...utils.filter import FilterBox, ProjectFilter
from ...utils.path import any_root
from ...utils.print import printer
from ...utils.scanner import ScanMode, SummaryFileMachine
from .. import _args as args
from .._engine import SafeTyper
from ._monitor import log_monitor
from ._scanner import folder_scanner


def main() -> None:
    app()


app = SafeTyper(name="tools", help="Basic equipment for development")


@app.command("monitor")
def launch_log_monitor_2(
    ctx: Context,
    file: args.LogFile = None,
    tail: bool = Option(True, help="Keep watching the file for new entries"),
):
    """Log Console Monitor: Analyze log file entries!"""

    config: ConfigManager = ctx.obj["config"]

    def render_adapter(dto: LogDTO):
        return printer.render(dto)  # LATER: improve adapter

    LogMonitorApp(
        log_file=file or config.log_result.struct_log_file,
        render_func=render_adapter,
        tail=tail,
    ).run()


@app.command("monitor1")
def launch_log_monitor_1(file: args.LogFile = None):  # TODO: improveCLI hint
    """Log Console Scroll: Watch new log file entries!"""
    log_monitor(log_path=file)


def enum_option(enum_class: type[Enum], default: Enum, help_text: str = ""):
    """
    Build Typer Option with auto-generated enum mapping

    - show: {num: Name} for all member, recognize by Name and select by number
    """
    # AI_TASK: this here is like broken, already default:Enum might be wrong
    mapping: str = ", ".join(
        [f"{member.value}: {member}" for member in enum_class]
    )
    full_help = f"{help_text} ({mapping})".strip()

    return typer.Option(default, help=full_help)


_filter_meta = args.enum_opt(FilterBox, "Select preset", "--filter")
_FilterArg = Annotated[FilterBox, _filter_meta]


@app.command("scanner")
def launch_folder_scanner(
    ctx: Context,
    scan_root: args.Root = None,
    output_file: args.OutputFile = None,
    file_type: SummaryFileMachine = SummaryFileMachine.MD,  # TODO: help text
    reset: args.CleanState = False,
    sort: TreeSelectorApp.Sort = TreeSelectorApp.Sort.SELECTION,
    filter_box: _FilterArg = FilterBox.PROJECT,
    scan_mode: ScanMode = ScanMode.RAW,
):
    """Folder Scanner with TreeSelector: Write combined file!"""
    system: System = ctx.obj["system"]
    paths: SstPaths = system.config.paths
    folder_scanner(
        scan_root=(root := scan_root or any_root()),
        output_file=output_file or paths.summary_file(suffix=file_type),
        cache_file=paths.scanner_cache_file(root),
        cache_reset=reset,
        sort=sort,
        local_printer=system.printer,
        filter=ProjectFilter.from_args(filter_box.args),
        scan_mode=scan_mode,
    )


@app.command("config")
def config_details_and_write(ctx: Context, write_config: args.Write = False):
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
