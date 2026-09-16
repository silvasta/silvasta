"""
Shape the View of the Classes

- view: attach configurable view to the decorated class
- ViewInjector: store and apply one view Mixin combination

- Cli, Log, Repr, Rich, Str: provide stable Mixin catalogue
  - Enums with a range of selected mixins

- views: all mixins atomized to single __dunder__
  - catalogue member and other implemented mixin

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

__all__: list[str] = [
    "view",
    "View",
    "ViewInjector",
    "ViewComposer",
]

from typing import TYPE_CHECKING as _TYPE_CHECKING

from ...port.shape import Injector
from ._compose import ViewComposer
from ._inject import ViewInjector
from ._preset import ViewPresets


class View(ViewInjector, ViewComposer, ViewPresets):
    """The Final assembled Decorator"""


view = View()

if _TYPE_CHECKING:
    _instance_check: Injector = view
    _class_check: type[Injector] = View
