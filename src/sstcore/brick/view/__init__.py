"""
Shape the View of the Classes

- view: attach configurable view to the decorated class
- ViewInjector: store and apply one view Mixin combination
- Cli, Log, Repr, Rich, Str: provide category Mixin selection
- views: provide all mixins as class with single __dunder__

Examples:
    @view(Cli.LINE, Str.SHORT)
    class Manual: ...

    @view.pydantic
    class Model(BaseModel): ...

    @view.pydantic.plus(cli=Cli.DEBUG)
    class Noisy(BaseModel): ...

    @view(Log.DATA, Repr.DEBUG, Cli.PANEL, Rich.NAME, Str.MODULE)
    class Full: ...
"""

from typing import TYPE_CHECKING

from sstcore.port.view import CliRenderable

__all__: list[str] = [
    "view",
    "ViewInjector",
    # enums
    "Cli",
    "Str",
    "Rich",
    "Repr",
    "Log",
    # all mixins
    "views",
]

from ...port.shape import Injector
from . import _mixin as views
from ._compose import ViewComposer
from ._inject import ViewInjector
from ._preset import ViewPresets
from ._registry import Cli, Log, Repr, Rich, Str


class _View(ViewInjector, ViewComposer, ViewPresets):
    """The Final assembled Decorator"""


view = _View()

if TYPE_CHECKING:
    _instance_check: Injector = view
    _class_check: type[Injector] = View


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### TESTS
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# REMOVE:
@view(Log.DATA, Repr.DEBUG, Cli.PANEL, Rich.NAME, Str.MODULE)
class Full: ...


# REMOVE:
class AnyView:
    def __str__(self):
        return "hello"


# REMOVE:
# AI_FOCUS: beside all this tests around, the .plus was the latest idea
# - including this directly in the protocol?
@view(Cli.HEADER, Rich.MODULE, Rich.NAME).plus(AnyView)
class Extended:
    x = 3


# REMOVE:
# REMOVE:
# REMOVE:
test1 = view(Cli.HEADER, Rich.MODULE, Rich.NAME).compose(AnyView)

test2: ViewInjector[type[Extended]] = ViewInjector(Cli.DEBUG)

class2 = test2.build()
instance = class2()
is_int = instance.x

test3: ViewInjector[type[CliRenderable]] = ViewInjector(Cli.HEADER)
class3 = test3.build("Class3")
to_print = class3()


@view(Cli.HEADER, Rich.MODULE, Rich.NAME).compose(AnyView)
class Extended2: ...
