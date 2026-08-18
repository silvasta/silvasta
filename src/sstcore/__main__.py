"""
Launch 'utils_app' with Example Functions

Amazing
- scanner: scan folder, select from filetree, merge to summary file

Useful
- monitor: Log Console with live updates from file
- print: Read Markdown and print with Rich

"""

from importlib.util import find_spec

from .port.functional import python_is_latest

#  AI: the python_is_latest is that simple:
#  def python_is_latest() -> bool:
#     return sys.version_info >= (3, 15)

if python_is_latest():
    lazy from rich.markup import escape  # ruff: noqa: UP036

    lazy from . import printer
    lazy from .bricks.color.box import Colors
    lazy from .cli import tools

else:

    def __getattr__(name: str):
        if name in lazy_map:
            from importlib import import_module

            return getattr(import_module(lazy_map[name], __name__), name)
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main() -> None:
    if cli_installed():
        tools()
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
    c = Colors()
    error: str = c.r("Problem with Installation")
    uv: str = c.b(f"uv add {sst_cli}")
    pip: str = c.b(f"pip install {sst_cli}")

    # scroll
    text: list[str] = [
        f"{error} Missing CLI dependency...",
        f"fix with {uv} {c.g('or')} {pip}",
    ]
    printer.danger(text)


lazy_map = {
    "SafeTyper": ".cli",
    "ConfigManager": ".config",
    "System": ".system",
    "Emitter": ".system.event",
    "PathGuard": ".utils.path.guard",
    "printer": ".utils.print",
}


if __name__ == "__main__":
    main()
