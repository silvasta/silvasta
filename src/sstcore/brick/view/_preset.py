"""
Collect and combine default Views

- ViewPresets: Support ViewInjector (maybe as mixin)

"""

# LATER: this thing will get very long...
# - defaults for regular classes
# - attach typing, e.g. by ViewComposer[MergedProtocol]

__all__: list[str] = [
    "ViewPresets",
]

from ._compose import ViewComposer
from ._inject import ViewInjector
from ._registry import Cli, Log, Repr, Rich, Str

# NEXT:
# NEXT:
# NEXT:
# NEXT:


class ViewPresets:  # WARN: return type?? ViewInjector needed? Self?
    pydantic = ViewInjector(
        cli=Cli.TABLE,
        string=Str.NAME,
        rich=Rich.MODULE,
        repr=Repr.OFF,
        log=Log.DATA,
    )

    printer = ViewComposer(
        cli=Cli.HEADER,
        string=Str.MODULE,
        rich=Rich.SHORT,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )

    safe_typer = ViewComposer(
        cli=Cli.PANEL,
        string=Str.SHORT,
        rich=Rich.MODULE,
        repr=Repr.DEBUG,
        log=Log.DEBUG,
    )
    functor = ViewComposer(
        cli=Cli.PANEL,
        string=Str.NAME,
        rich=Rich.MODULE,
        log=Log.DEBUG,
        repr=Repr.DATA,
    )
