"""
Launch cli_tools with SafeTyper and the full System in action

Amazing
- scanner: Select in tui filetree from scanned folder and merge to summary file

Useful
- monitor: Log Console with live updates from file (new with .jsonl)
- print: Read Markdown and print with Rich

"""

from . import printer
from .console.tools import cli_tools


def main() -> None:
    if cli_installed():
        cli_tools()
    else:
        install_instructions()


def cli_installed() -> bool:
    # REMOVE: when new ImportError setup works
    from importlib.util import find_spec

    def _installed(package: str):
        return find_spec(name=package) is not None

    return all(_installed(package) for package in ["typer", "textual"])


def install_instructions():
    # LATER: this as well for sstcore.__init__, and maybe others
    from rich.markup import escape

    from .brick.color.box import Colors

    sst_cli: str = escape("'sstcore[cli]'")
    colors = Colors()
    error: str = colors.red("Problem with Installation")
    uv: str = colors.b(f"uv add {sst_cli}")
    pip: str = colors.blue(f"pip install {sst_cli}")

    text: list[str] = [  # scroll
        f"{error} Missing CLI dependency...",
        f"fix with {uv} {colors.g('or')} {pip}",
    ]
    printer.danger(text)


# TASK: probably in .__init__
# def __getattr__(name: str):
#     if name in _LAZY_IMPORTS:
#         module_path = _LAZY_IMPORTS[name]
#         try:
#             module = import_module(module_path, package=__package__)
#             return getattr(module, name)
#         except ImportError as e:
#             # Intercept missing optional dependencies gracefully
#             if name == "SafeTyper":
#                 raise ImportError(
#                     f"\nMissing CLI dependencies for {name}.\n"
#                     "Fix with: uv add 'sstcore-py[cli]' or pip install 'sstcore-py[cli]'"
#                 ) from e
#             raise  # Re-raise standard import errors for other modules
#     raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

if __name__ == "__main__":
    main()
