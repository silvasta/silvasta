import typer

from sstcore import printer
from sstcore.tui import ListSelectorApp

app = typer.Typer()


@app.command()
def process_list(
    multi_selct: bool = typer.Option(
        False, "--multi", "-m", help="Select multiple items"
    ),
    example: int = typer.Option(
        False, "--example", "-e", help="1:list, 2:dict,..."
    ),
):
    """Process a specific item from a list."""

    match example:
        case 1:
            options = ["server-alpha", "server-beta", "server-gamma"]
        case 2:
            options = {"id1": "Alpha Database", "id2": "Beta Database"}
        case _:
            options = {"id1": "Alpha Database", "id2": "Beta Database"}

    tui = ListSelectorApp(items=options, multi_select=multi_selct)
    selected_items: list | None = tui.run()

    if not selected_items:
        printer.warn("Action cancelled by user.")
        raise typer.Exit()

    printer.lines_with_len("Select", lines=selected_items)


if __name__ == "__main__":
    app()
