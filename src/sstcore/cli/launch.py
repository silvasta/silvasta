from pathlib import Path

from ..tui import TreeSelectorApp
from ..utils.print import printer
from . import args as sargs
from .engine import SafeTyper
from .monitor import log_monitor
from .scanner import folder_scanner


def main() -> None:
    utils_app()


utils_app = SafeTyper(
    name="utils",
    help="FolderScanner and Log Console Monitor",
)


@utils_app.command("monitor")
def launch_monitor(file: sargs.File = None):  # NOTE: CLI hint not amazing...
    """Log Console Monitor: watch new log file entries"""
    log_monitor(log_path=file)


@utils_app.command("scanner")
def launch_folder_scanner(
    scan_root: sargs.Root = None,
    output_file: sargs.File = None,
    sort: TreeSelectorApp.Sort = TreeSelectorApp.Sort.BY_SELECTION,
):
    """Folder Scanner with TreeSelector: write combined file"""
    folder_scanner(scan_root, output_file, sort_method=sort)


@utils_app.command("print")
def print_file(path: Path):
    """Print Prompt, Response or any Markdown File in Rich style"""
    printer.title(path.name)
    match path.suffix:
        case ".json":
            printer(path.read_text())
        case ".md":
            printer.md(path.read_text())
        case _:
            # LATER: other file types?
            # match as function of printer ?!
            # printer.file(*.xx) dispatches xx
            printer.md(path.read_text())


if __name__ == "__main__":
    main()
