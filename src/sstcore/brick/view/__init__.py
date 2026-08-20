"""
Shape the View of the Classes

- view: attach configurable view to the decorated class
- ViewBuilder: store and apply one view Mixin combination
- Cli, Log, Repr, Rich, Str: provide category Mixin selection
- views: provide all mixins as class with single __dunder__

Examples:
    @view(Cli.LINE, Str.SHORT)
    class Manual: ...

    @view.pydantic
    class Model(BaseModel): ...

    @view.pydantic.evolve(cli=Cli.DEBUG)
    class Noisy(BaseModel): ...

    @view(Log.DATA, Repr.DEBUG, Cli.PANEL, Rich.NAME, Str.MODULE)
    class Full: ...
"""

from sstcore.port.view import CliRenderable

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


# REMOVE:
@view(Log.DATA, Repr.DEBUG, Cli.PANEL, Rich.NAME, Str.MODULE)
class Full: ...


# REMOVE:
class AnyView:
    def __str__(self):
        return "hello"


# REMOVE:
@view(Cli.HEADER, Rich.MODULE, Rich.NAME).plus(AnyView)
class Extended:
    x = 3


# REMOVE:
# REMOVE:
# REMOVE:
test1 = view(Cli.HEADER, Rich.MODULE, Rich.NAME).compose(AnyView)

test2: ViewBuilder[type[Extended]] = ViewBuilder(Cli.DEBUG)

class2 = test2.build()
instance = class2()
is_int = instance.x

test3: ViewBuilder[type[CliRenderable]] = ViewBuilder(Cli.HEADER)
class3 = test3.build("Class3")
to_print = class3()


@view(Cli.HEADER, Rich.MODULE, Rich.NAME).compose(AnyView)
class Extended2: ...
