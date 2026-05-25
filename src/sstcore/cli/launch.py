from pathlib import Path

import typer

from ..config import ConfigManager, get_config
from ..tui import TreeSelectorApp
from ..utils.print import printer
from . import args as sargs
from .monitor import log_monitor
from .scanner import folder_scanner
from .setup import attach_callback, logger_catch


def launch_monitor(file: sargs.File = None):  # NOTE: CLI hint not amazing...
    """Log Console Monitor: watch new log file entries"""
    log_monitor(log_path=file)


@logger_catch
def launch_folder_scanner(
    scan_root: sargs.Root = None,
    output_file: sargs.File = None,
    sort: TreeSelectorApp.Sort = TreeSelectorApp.Sort.BY_SELECTION,
):
    """Folder Scanner with TreeSelector: write combined file"""
    folder_scanner(scan_root, output_file, sort_method=sort)


def config_details():
    """Print config and paths to Console, use --write for new file"""
    # IMPORTANT: use config from derived project, setup config?
    config: ConfigManager = get_config()

    printer(config.settings)
    printer(config.setting_file)
    # printer(config.paths.dot_env) INFO: raises Error and creates empty default if file not exists


def print_file(path: Path):
    """Print Prompt, Response or any Markdown File in Rich style"""
    printer.title(path.name)
    match path.suffix:
        case ".json":
            printer(path.read_text())
        case ".md":
            printer.md(path.read_text())
        case _:  # LATER: other file types? match as function of printer!?
            printer.md(path.read_text())


def main() -> None:
    app()


app = typer.Typer(
    name="utils",
    help="Show statistics, configurations and more",
    no_args_is_help=True,
)
attach_callback(app)

app.command("monitor")(launch_monitor)
app.command("scanner")(launch_folder_scanner)
app.command("config")(config_details)
app.command("print")(print_file)

if __name__ == "__main__":
    main()
