"""
Launch cli_tools with SafeTyper and the full System in action

Amazing
- scanner: Select in tui filetree from scanned folder and merge to summary file

Useful
- monitor: Log Console with live updates from file (new with .jsonl)
- print: Read Markdown and print with Rich

"""

from importlib.util import find_spec

from rich.markup import escape

from . import printer
from .brick.color.box import Colors
from .console.tools import cli_tools


def main() -> None:
    if cli_installed():
        cli_tools()
    else:
        install_instructions()


def cli_installed() -> bool:
    # MOVE: maybe to python_is_latest? list[str] input for all checks

    def _installed(package: str):
        # MOVE: maybe to python_is_latest? str input for 1 check
        return find_spec(name=package) is not None

    return all(_installed(package) for package in ["typer", "textual"])


def install_instructions():
    sst_cli: str = escape("'sstcore[cli]'")
    colors = Colors()
    error: str = colors.red("Problem with Installation")
    uv: str = colors.b(f"uv add {sst_cli}")
    pip: str = colors.blue(f"pip install {sst_cli}")

    # scroll
    text: list[str] = [
        f"{error} Missing CLI dependency...",
        f"fix with {uv} {colors.g('or')} {pip}",
    ]
    printer.danger(text)


if __name__ == "__main__":
    main()
