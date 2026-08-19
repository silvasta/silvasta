"""
Define common Views and Defaults

- view: universal tool

"""

# TODO: defaults for regular classes

__all__: list[str] = [
    "view",
]

from ._compose import ViewBuilder
from ._registry import Cli, Log, Repr, Rich, Str

type ViewArg = Cli | Str | Rich | Repr | Log


class ViewError(CoreError): ...


class _View:
    """Distribute ViewBuilder with Presets"""

    def __call__(
        self,
        *args: ViewArg,
        cli: Cli = Cli.OFF,
        str: Str = Str.OFF,
        rich: Rich = Rich.OFF,
        repr: Repr = Repr.OFF,
        log: Log = Log.OFF,
    ) -> ViewBuilder:

        kwargs = {
            "cli": cli,
            "str": str,
            "rich": rich,
            "repr": repr,
            "log": log,
        }

        # 2. Process positional args dynamically based on their type
        for arg in args:
            if isinstance(arg, Cli):
                kwargs["cli"] = arg
            elif isinstance(arg, Str):
                kwargs["str"] = arg
            elif isinstance(arg, Rich):
                kwargs["rich"] = arg
            elif isinstance(arg, Repr):
                kwargs["repr"] = arg
            elif isinstance(arg, Log):
                kwargs["log"] = arg
            else:
                raise TypeError(
                    f"Invalid view argument type: {type(arg).__name__}"
                )

        return ViewBuilder(**kwargs)
        # return ViewBuilder(cli=cli, str=str, rich=rich, repr=repr, log=log)

    pydantic = ViewBuilder(
        cli=Cli.TABLE,
        string=Str.NAME,
        rich=Rich.MODULE,
        repr=Repr.OFF,
        log=Log.DATA,
    )

    printer = ViewBuilder(
        cli=Cli.HEADER,
        string=Str.MODULE,
        rich=Rich.SHORT,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )

    safe_typer = ViewBuilder(
        cli=Cli.PANEL,
        string=Str.SHORT,
        rich=Rich.MODULE,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )
    functor = ViewBuilder(
        cli=Cli.PANEL,
        string=Str.NAME,
        rich=Rich.MODULE,
        log=Log.DEBUG,
        repr=Repr.DATA,
    )


view = _View()
