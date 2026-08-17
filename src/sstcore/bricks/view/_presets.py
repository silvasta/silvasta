"""
Define common Views and Defaults

- view: universal tool

"""

__all__: list[str] = [
    "view",
]

from ._compose import ViewBuilder
from ._registry import Cli, Log, Repr, Rich, Str

# TODO: defaults for regular classes


class _View:
    """Distribute ViewBuilder with Presets"""

    def __call__(
        self,
        cli: Cli = Cli.OFF,
        str: Str = Str.OFF,
        rich: Rich = Rich.OFF,
        repr: Repr = Repr.OFF,
        log: Log = Log.OFF,
    ) -> ViewBuilder:
        return ViewBuilder(cli=cli, str=str, rich=rich, repr=repr, log=log)

    pydantic = ViewBuilder(
        cli=Cli.TABLE,
        str=Str.NAME,
        rich=Rich.MODULE,
        repr=Repr.OFF,
        log=Log.DATA,
    )

    printer = ViewBuilder(
        cli=Cli.HEADER,
        str=Str.MODULE,
        rich=Rich.SHORT,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )

    safe_typer = ViewBuilder(
        cli=Cli.PANEL,
        str=Str.SHORT,
        rich=Rich.MODULE,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )


view = _View()
