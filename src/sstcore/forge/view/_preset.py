"""
Collect and combine default Views

- ViewPresets: Support ViewInjector (maybe as mixin)

"""

__all__: list[str] = [
    "ViewPresets",
]

from ._compose import ViewInjector
from .catalog import Cli, Log, Repr, Rich, Str


class ViewPresets:
    pydantic = ViewInjector(
        cli=Cli.TABLE,
        string=Str.NAME,
        rich=Rich.MODULE,
        repr=Repr.OFF,
        log=Log.DATA,
    )

    printer = ViewInjector(
        cli=Cli.HEADER,
        string=Str.MODULE,
        rich=Rich.SHORT,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )

    safe_typer = ViewInjector(
        cli=Cli.PANEL,
        string=Str.SHORT,
        rich=Rich.MODULE,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )

    functor = ViewInjector(
        cli=Cli.PANEL,
        string=Str.NAME,
        rich=Rich.MODULE,
        log=Log.DEBUG,
        repr=Repr.DATA,
    )
