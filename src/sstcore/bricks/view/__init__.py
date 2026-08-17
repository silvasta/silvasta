"""
Shape the View of the Classes

- view: attach configurable view to the decorated class
- ViewBuilder: store and apply one view Mixin combination
- Cli, Log, Repr, Rich, Str: provide category Mixin selection
- views: provide all mixins as class with single __dunder__

Examples:
    @view(cli=Cli.LINE, str=Str.SHORT)
    class Manual: ...

    @view.pydantic
    class Model(BaseModel): ...

    @view.pydantic.evolve(cli=Cli.DEBUG)
    class Noisy(BaseModel): ...

"""

__all__: list[str] = [
    "view",
    "ViewBuilder",
    # enums
    "Cli",
    "Str",
    "Rich",
    "Repr",
    "Log",
    # all mixins
    "views",
]

from . import _mixin as views
from ._compose import ViewBuilder
from ._presets import view
from ._registry import Cli, Log, Repr, Rich, Str
