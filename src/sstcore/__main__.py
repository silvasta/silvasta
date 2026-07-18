"""
Launch 'utils_app' with Example Functions

Amazing
- scanner: scan folder, select from filetree, merge to summary file

Useful
- monitor: Log Console with live updates from file
- print: Read Markdown and print with Rich

"""

import importlib.util
import sys

from rich.markup import escape

from . import printer


def main() -> None:
    check_cli_installed()
    from .cli import tools

    tools()


def check_cli_installed():
    """Find required packages or give instructions and quit"""

    cli_is_installed: bool = (
        importlib.util.find_spec("typer") is not None
        and importlib.util.find_spec("textual") is not None
    )

    if not cli_is_installed:
        # paint
        error: str = printer.color_box.red("Problem with Installation")
        sst_cli = escape("'sstcore[cli]'")
        uv: str = printer.color_box.cyan(f"uv add {sst_cli}")
        or_: str = printer.color_box.green("or")
        pip: str = printer.color_box.cyan(f"pip install {sst_cli}")

        # scroll
        text: list[str] = [
            f"{error} Missing CLI dependency...",
            f"fix with {uv} {or_} {pip}",
        ]
        printer.danger(text)

        sys.exit(1)


def check_cli_installed():
    """Find required packages or give instructions and quit"""

    cli_installed = (
        importlib.util.find_spec("typer") is not None
        and importlib.util.find_spec("textual") is not None
    )

    if not cli_installed:
        # paint
        error: str = printer.colors.red("Problem with Installation")
        _sst = escape("'sstcore[cli]'")
        uv: str = printer.colors.cyan(f"uv add {_sst}")
        or_: str = printer.colors.green("or")
        pip: str = printer.colors.cyan(f"pip install {_sst}")

        # canvas
        text: list[str] = [
            f"{error} Missing CLI dependency...",
            f"fix with {uv} {or_} {pip}",
        ]
        printer.danger(text)

        sys.exit(1)


if __name__ == "__main__":
    main()
