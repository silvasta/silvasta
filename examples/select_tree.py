import typer

from silvasta.tui.tree_selector import TreeSelectorApp
from silvasta.utils import printer
from silvasta.utils.simple_tree import SimpleTreeNode, get_example_tree

example_tree: SimpleTreeNode = get_example_tree()

app = typer.Typer()


@app.command()
def process_tree(
    target_node: str = typer.Argument(
        None, help="The exact ID/name of the node to process"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Use TUI picker"
    ),
):
    """Process a specific node in the forest."""

    if interactive:
        tui = TreeSelectorApp(tree_data=example_tree)
        selected_node: str | None = tui.run()

        if not selected_node:
            printer.warn("Action cancelled by user.")
            raise typer.Exit()

        target_node: str = selected_node

    elif target_node is None:
        printer.danger(
            "You must provide a target_node or use the --interactive flag!"
        )
        raise typer.Exit(code=1)

    printer.success(f"Successfully selected node: {target_node}")


if __name__ == "__main__":
    app()
