from enum import StrEnum, auto
from pathlib import Path

import typer

from sstcore.config import ConfigManager, get_config
from sstcore.tui.tree_selector import TreeSelectorApp
from sstcore.utils import FolderScanner, ProjectFilter, printer
from sstcore.utils.path import find_project_root

config: ConfigManager = get_config()

SCAN_ROOT: Path = find_project_root()
OUTPUT_FILE: Path = config.paths.summary_file()


PATH_FILTER = ProjectFilter(
    _debug=False,
    # exclude=set(), # take care while overriding defaults
    require_any={
        "paths",
        "names",
    },
)


class Tasks(StrEnum):
    PICK = auto()
    FILTER = auto()
    # TODO: memorize the last pick?

    @property
    def scanner(self) -> FolderScanner:
        match self:
            case Tasks.PICK:
                return FolderScanner(scan_root=SCAN_ROOT)
            case Tasks.FILTER:
                return FolderScanner(
                    scan_root=SCAN_ROOT, path_filter=PATH_FILTER
                )


app = typer.Typer()


@app.command()
def process_tree(task: Tasks = Tasks.PICK):
    """Process a specific node in the forest."""

    scanner: FolderScanner = task.scanner
    tui = TreeSelectorApp(sst_tree=scanner.filesystem_tree())
    selected_nodes: list | None = tui.run()

    if not selected_nodes:
        printer.warn("Action cancelled by user.")
        raise typer.Exit()

    printer.title(f"{type(selected_nodes[0])=}")
    printer.lines_with_len(
        name="Successfully selected nodes",
        lines=selected_nodes,
    )
    summary_file: Path = scanner._summary_file(
        local_root=SCAN_ROOT,
        files=selected_nodes,
        output_file=OUTPUT_FILE,
    )
    printer.lines(header="Summary File written to:", lines=[summary_file])


if __name__ == "__main__":
    app()
