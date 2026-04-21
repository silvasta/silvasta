from pathlib import Path

import typer

from silvasta.tui.tree_selector import TreeSelectorApp
from silvasta.utils import FolderScanner, printer
from silvasta.utils.path import find_project_root
from silvasta.utils.simple_tree import (
    SimpleTreeNode,
    get_big_example_tree,
    get_example_tree,
)

SCAN_ROOT: Path = find_project_root()


def select_example_tree(
    task=2,  # TODO: select loaded tree here
) -> SimpleTreeNode:

    trees: list[SimpleTreeNode] = [
        get_example_tree(),
        get_big_example_tree(),
        FolderScanner.tree(root=SCAN_ROOT),
    ]
    return trees[task]


app = typer.Typer()


@app.command()
def process_tree(
    target_node: str | None = typer.Option(
        None, help="The exact ID/name of the node to process"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Use TUI picker"
    ),
):
    """Process a specific node in the forest."""

    if interactive:
        tui = TreeSelectorApp(sst_tree=select_example_tree())
        selected_nodes: list | None = tui.run()

        if not selected_nodes:
            printer.warn("Action cancelled by user.")
            raise typer.Exit()

        target_node: list = selected_nodes

    elif target_node is None:
        printer.danger(
            "You must provide a target_node or use the --interactive flag!"
        )
        raise typer.Exit(code=1)

    printer.success(f"Successfully selected node: {target_node}")


if __name__ == "__main__":
    app()
