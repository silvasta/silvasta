"""
Shape the View of the Classes

- view: attach configurable view to the decorated class
- ViewComposer: combined Builder and Injector with Presets

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
    "ViewBuilder",
    "ViewInjector",
    "ViewComposer",
    "catalog",
    "views",
]


from ...port.link import portlink as _portlink
from ...port.shape import Injector
from . import _views as views
from . import catalog
from ._compose import ViewBuilder, ViewInjector
from ._preset import ViewPresets


@_portlink(Injector)
class ViewComposer(ViewInjector, ViewBuilder, ViewPresets):
    """The Final assembled Decorator"""


view = ViewComposer()

if __name__ == "__main__":
    from .catalog import Cli, Log, Repr, Rich, Str

    class Dummy1: ...

    view(Dummy1, Cli.DEBUG)

    @view.printer
    class Dummy2: ...

    @view.functor
    class Dummy3: ...

    @view(Cli.DEBUG, Log.DEBUG, Str.NAME, Repr.DEBUG, Rich.OFF)
    class Dummy4: ...

    @view.functor.plus(Cli.DEBUG)
    class Dummy5: ...

    @view()
    class Dummy6: ...
