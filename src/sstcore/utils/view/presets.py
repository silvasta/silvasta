"""
Define common Views and Defaults

- build_print_view: Default for Printer

"""

__all__: list[str] = [
    "printer_view_builder",
]

from .compose import ViewBuilder
from .registry import Cli, Log, Repr, Rich, Str


def printer_view_builder() -> ViewBuilder:
    return ViewBuilder(
        cli=Cli.BAR,
        str=Str.DEFAULT,
        rich=Rich.SHORT,
        repr=Repr.DEFAULT,
        log=Log.FULL,
    )
