from pathlib import Path

from ..tui import TreeSelectorApp
from ..utils.print import printer
from . import args as sargs
from .engine import SafeTyper
from .monitor import log_monitor
from .scanner import folder_scanner

# TODO: Rename utils_app or similar


def main() -> None:
    app()


app = SafeTyper(
    name="utils",
    help="Show statistics, configurations and more",
)


def launch_monitor(file: sargs.File = None):  # NOTE: CLI hint not amazing...
    """Log Console Monitor: watch new log file entries"""
    log_monitor(log_path=file)


def launch_folder_scanner(
    scan_root: sargs.Root = None,
    output_file: sargs.File = None,
    sort: TreeSelectorApp.Sort = TreeSelectorApp.Sort.BY_SELECTION,
):
    """Folder Scanner with TreeSelector: write combined file"""
    folder_scanner(scan_root, output_file, sort_method=sort)


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


app.command("monitor")(launch_monitor)
app.command("scanner")(launch_folder_scanner)
app.command("print")(print_file)

if __name__ == "__main__":
    main()
