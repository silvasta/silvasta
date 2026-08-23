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
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:

from typing import TYPE_CHECKING, Self, overload

from ...brick.forge.mix import MixinRegistry
from ...port.register import MixinRegister
from ...port.shape import Injector
from ._compose import ViewComposer
from ._raise import ViewError
from ._registry import Cli, Log, Repr, Rich, Str, ViewRegistry

# MOVE: to view._registry
type ViewArg = Cli | Str | Rich | Repr | Log


class ViewInjector[MixT: type]:
    """view Distributor: Inject or Build with Preset Views or Modify"""

    mixins: tuple[type, ...]
    vault: MixinRegister[MixT]

    def __init__(self):
        # AI: maybe function that loads the mixin registry  from Composer.mixins?
        self.mixin_registger: MixinRegister[MixT] = MixinRegistry(self.mixins)
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
        cli: Cli = Cli.OFF,
        string: Str = Str.OFF,
        rich: Rich = Rich.OFF,
        repr: Repr = Repr.OFF,
        log: Log = Log.OFF,
    ) -> Self:  # AI: Self???

        selected_views: dict[str, ViewRegistry] = {}

        for arg in args:
            if arg.category in selected_views:
                raise ViewError(arg.fail_info("Duplicated Argument!"))
            selected_views[arg.category] = arg
        # AI: here maybe collect all incomming, and create only 1 time a new tuple?

        for default in self.all_enums():
            if default.category not in selected_views:
                selected_views[default.category] = default

        return ViewComposer(**selected_views)  # ty:ignore -- shows arg fail

    def plus(self, *args, **kwargs):
        raise NotImplementedError


if TYPE_CHECKING:
    _instance_check: Injector = ViewComposer()
    _class_check: type[Injector] = ViewComposer
