"""
Shape the View of the Classes

- view: attach configurable view to the decorated class
- ViewInjector: store and apply one view Mixin combination

- Cli, Log, Repr, Rich, Str: provide stable Mixin catalogue
  - Enums with a range of selected mixins

- views: provide all mixins classes with single __dunder__
  - all catalogue member plus any other not selected mixin

Examples:
    @view(Cli.LINE, Str.SHORT)
    class Manual: ...

    @view.pydantic
    class Model(BaseModel): ...

    @view.pydantic.plus(cli=Cli.DEBUG)
    class Noisy(BaseModel): ...

    @view(Log.DATA, Repr.DEBUG, Cli.PANEL, Rich.NAME, Str.MODULE)
    class Full: ...

Catalogue:
  Enum   : Implemented Mixin Method
  - Cli  : __cli__
  - Str  : __str__
  - Rich : __rich__
  - Repr : __repr__
  - Log  : __log__
"""

from typing import TYPE_CHECKING

from sstcore.port.event.dto import CliRenderable

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
    _class_check: type[Injector] = _View


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


# REMOVE: when adapted, especially .plus
@view(Cli.HEADER, Rich.MODULE, Rich.NAME).plus(AnyView)
class Extended:
    x = 3


# REMOVE:
test1 = view(Cli.HEADER, Rich.MODULE, Rich.NAME).plus(AnyView)
test2: ViewInjector[type[Extended]] = view(Cli.DEBUG)
class2 = test2.build()
instance = class2()
is_int = instance.x
test3: ViewInjector[type[CliRenderable]] = view(Cli.HEADER)
class3 = test3.build("Class3")
to_print = class3()


# REMOVE:
@view(Cli.HEADER, Rich.MODULE, Rich.NAME).plus(AnyView)
class Extended2: ...
