from typing import Any, Self, overload

from ....port.link import portlink
from ....port.shape import Injector
from ....port.solid import MixinCatalog
from ._builder import MixinBuilder

__all__: list[str] = [
    "MixInjector",
]


@portlink(Injector)
class MixInjector(MixinBuilder):
    """Generic Routing Layer for Decorators."""

    @overload
    def __call__[Cls: type](self, cls: Cls, /) -> Cls: ...
    @overload
    def __call__[Cls: type, Mix](self, cls: Cls, /, *mixins: Mix) -> Cls: ...
    @overload
    def __call__(self, *mixins: Any) -> Self: ...

    def __call__[Cls: type, Mix: type | MixinCatalog](
        self, cls: Cls | None = None, /, *mixins: Mix
    ) -> Any:

        match cls, mixins:
            case None, ():
                return self
            case None, _:
                return self.plus(*mixins)
            case type() as target, ():
                return self.inject(target)
            case type() as target, _:
                return self.plus(*mixins).inject(target)

    def plus[Mix: type | MixinCatalog](self, *mixins: Mix) -> Self:
        raise NotImplementedError(f"Cannot process: {mixins=}")
