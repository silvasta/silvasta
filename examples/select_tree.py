from enum import Enum
from pathlib import Path

import typer

from sstcore.tui.tree_selector import TreeSelectorApp
from sstcore.utils import FolderScanner, SimpleTreeNode, printer
from sstcore.utils.path import find_project_root
from sstcore.utils.simple_tree import (
    get_big_example_tree,
    get_example_tree,
)

SCAN_ROOT: Path = find_project_root()


class Tasks(Enum):
    Example_Tree = "tree"
    BIG_Example_Tree = "big"
    SCAN = "scan"

    def tree(self) -> SimpleTreeNode:
        match self:
            case Tasks.Example_Tree:
                return get_example_tree()
            case Tasks.BIG_Example_Tree:
                return get_big_example_tree()
            case Tasks.SCAN:
                return FolderScanner.tree(root=SCAN_ROOT)


app = typer.Typer()


@app.command()
def process_tree(task: Tasks = Tasks.SCAN):
    """Process a specific node in the forest."""

    tui = TreeSelectorApp(sst_tree=task.tree())
    selected_nodes: list | None = tui.run()

    if not selected_nodes:
        printer.warn("Action cancelled by user.")
        raise typer.Exit()

    printer.lines_with_len(
        name="Successfully selected nodes",
        lines=selected_nodes,
    )


if __name__ == "__main__":
    app()
