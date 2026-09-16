"""
Collect and combine default Views

- ViewPresets: Support ViewInjector (maybe as mixin)

"""

# LATER: this thing will get very long...
# - defaults for regular classes
# - attach typing, e.g. by ViewBuilder[MergedProtocol]

__all__: list[str] = [
    "ViewPresets",
]

from ...brick.views import Cli, Log, Repr, Rich, Str
from ._compose import ViewBuilder
from ._inject import ViewInjector

# NEXT:
# NEXT:
# NEXT:
# NEXT:


class ViewPresets:  # WARN: return type?? ViewInjector needed? Self?
    pydantic = ViewInjector(
        # FIX:
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
