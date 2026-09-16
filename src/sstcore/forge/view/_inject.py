"""
Define common Views and Defaults

- view: universal tool

"""

# TODO: defaults for regular classes

__all__: list[str] = [
    "ViewInjector",
]
# NEXT:
# NEXT:

from typing import TYPE_CHECKING, Self, overload

from ...brick.none import Ghost
from ._compose import ViewBuilder

if TYPE_CHECKING:

    class _MixInjector(ViewBuilder): ...
else:
    _MixInjector = Ghost

from ...brick.views import Cli, Log, Repr, Rich, Str, ViewCatalog
from ...port.register import MixinRegister
from ...port.shape import Injector
from .._raise import ViewError
from ..engine.compose import MixinRegistry

# MOVE: to view._registry
type ViewArg = Cli | Str | Rich | Repr | Log


class ViewInjector[MixT: type, KeyT](_MixInjector):
    """view Distributor: Inject or Build with Preset Views or Modify"""

    vault: MixinRegister[MixT, KeyT]

    def __init__(self):
        self.mixin_registger = MixinRegistry(self.mixins)
        super().__init__()

    @overload
    def __call__[Target: type](self, cls: Target, /) -> Target: ...

    @overload
    def __call__(self, /) -> MixT: ...

    @overload
    def __call__(self, *args: ViewArg, **kwargs: ViewArg) -> Self: ...

    def __call__(
        self,
        *args: ViewArg,  # LATER: allow for mixins not in Enum registries
        _cli: Cli = Cli.OFF,  # TEST: view in IDE
        _string: Str = Str.OFF,
        _rich: Rich = Rich.OFF,
        _repr: Repr = Repr.OFF,
        _log: Log = Log.OFF,
    ) -> Self:  # AI: Self???

        selected_views: dict[str, ViewCatalog] = {}

        # NEXT:
        # NEXT:
        # TODO: decompose
        for arg in args:
            if arg.category in selected_views:
                raise ViewError(arg.fail_info("Duplicated Argument!"))
            selected_views[arg.category] = arg

        for default in self.all_enums():
            if default.category not in selected_views:
                selected_views[default.category] = default

        return ViewBuilder(**selected_views)  # ty:ignore -- shows arg fail

    def plus(self, *args, **kwargs):
        raise NotImplementedError


if TYPE_CHECKING:
    _instance_check: Injector = ViewBuilder()
    _class_check: type[Injector] = ViewBuilder
