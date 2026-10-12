"""
Compose Views at runtime and inject them into target Classes

- ViewBuilder: regular compostion
- ViewInjector: hybrid decorator

"""

__all__: list[str] = [
    "ViewBuilder",
    "ViewInjector",
]


from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self

from ...brick.none import ViewSentinel
from ...port.link import portlink
from ...port.raising import SstCoreError
from ...port.shape import Builder, Injector
from ...port.solid import MixinCatalog
from ..compose import MixinBuilder, MixInjector
from .catalog import Cli, Log, Repr, Rich, Str

type ViewArg = Cli | Str | Rich | Repr | Log  # MOVE: to view._registry?


@portlink(Builder)
@dataclass(frozen=True)
class ViewBuilder[ViewBase: type](MixinBuilder):
    """Configure ViewMixin sets and build composed classes"""

    cli: Cli = Cli.OFF
    log: Log = Log.OFF
    repr: Repr = Repr.OFF
    string: Str = Str.OFF
    rich: Rich = Rich.OFF

    def evolve(self, **changes: Any) -> Self:
        """Copy with overrides"""
        return replace(self, **changes)

    def all_enums(
        self,
    ) -> tuple[Cli, Log, Repr, Str, Rich]:
        """Provide all attached ViewRegistry member"""
        return (self.cli, self.log, self.repr, self.string, self.rich)

    @cached_property
    def mixins(self) -> tuple[type, ...]:
        return tuple(
            mixin
            for category in self.all_enums()
            if (mixin := category.mixin) is not ViewSentinel
        )

    @property
    def _topic_name(self) -> str:
        return "View"


@portlink(Injector)
@dataclass(frozen=True)
class ViewInjector[MixT: type](MixInjector, ViewBuilder):
    """view Distributor: Inject or Build with Preset Views or Modify"""

    # LATER: accept as well "free" mixins, without ViewCatalog coupling

    def plus(self, *mixins: ViewArg) -> Self:
        """Update existing View spec and return new specialized Injector"""

        selected_views: dict[str, ViewArg] = {}

        for item in mixins:
            MixinCatalog.resolve(item)
            if item.category in selected_views:
                # LATER: on fail? maybe skip, definitely other error!
                raise SstCoreError(f"{item}: Duplicated! {selected_views=}")
            selected_views[item.category] = item

        return self.evolve(**selected_views)
