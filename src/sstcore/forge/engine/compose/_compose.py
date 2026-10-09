"""
Define the Abstract Shape of the Composer

-
"""

# NEXT: finish builder

__all__: list[str] = [
    "MixinComposer",
]

from typing import Any, cast, overload

from ....port.link import portlink
from ....port.shape import Builder, Mixins
from . import _mixer as mix
from ._vault import MixinRegistry


@portlink(Builder)
class MixinComposer[MixT: type]:
    """The Generic Engine for Class Assembly"""

    @property
    def mixins(self) -> Mixins:
        """Provide all selected Mixins"""
        raise NotImplementedError

    def __init__(self, vault: MixinRegistry):
        self.vault: MixinRegistry = vault

    def mix_name(self, name: str = "") -> str:
        """Resolve the name of the new dynamically created class."""
        raise NotImplementedError(name)

    def mix(self, name: str = "", extras: dict | None = None) -> MixT:
        """Create a completely new class from the registry's mixins."""
        clsname: str = self.mix_name(name)
        namespace: dict[str, Any] = mix.NameSpace.prepare1(extras=extras)
        new_cls = type(clsname, self.vault.mixins, namespace)
        return cast(MixT, new_cls)

    def inject[TargeT: type](
        self,
        cls: type,
        prepend: bool = True,
        extras: dict | None = None,
        **kwargs,
    ) -> TargeT:
        """Inject the registry's mixins into an existing cls class."""
        # Mixins go before the cls for overrides, after for fallbacks

        bases: tuple[type, ...] = (
            self.vault.mixins + (cls,)
            if prepend
            else (cls,) + self.vault.mixins
        )

        clsname: str = self.mix_name(cls.__name__)
        namespace: dict[str, Any] = mix.NameSpace.prepare1(cls, extras)
        new_cls = type(clsname, bases, namespace)

        return cast(typ=TargeT, val=new_cls)

    @overload
    def compose[TargeT: type](self, cls: type, mixins: Mixins) -> TargeT: ...
    @overload
    def compose[TargeT: type](self, mixins: Mixins) -> TargeT: ...
    def compose[TargeT: type](
        self,
        cls: TargeT | None = None,
        mixins: Mixins | None = None,
        **kwargs: Any,
    ) -> TargeT | MixT:
        """Dispatch to build or inject based on input."""
        if cls is None:
            return self.mix(**kwargs)
        return self.inject(cls, **kwargs)
