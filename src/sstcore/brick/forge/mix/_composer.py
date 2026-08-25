"""
Define the Abstract Shape of the Composer

-
"""

__all__: list[str] = [
    "MixinComposer",
]

from typing import Any, cast

from . import _mixer as mix
from ._vault import MixinRegistry

# NEXT:
# NEXT:
# NEXT:
# NEXT:
# NEXT:


class MixinComposer[MixT: type]:
    """The Generic Engine for Class Assembly"""

    def __init__(self, vault: MixinRegistry):
        self.vault: MixinRegistry = vault

    def _generate_name(self, **kwargs) -> str:
        """Resolve the name of the new dynamically created class."""
        raise NotImplementedError

    def build(self, name: str = "", extras: dict | None = None) -> MixT:
        """Create a completely new class from the registry's mixins."""
        cls_name: str = self._generate_name(override_name=name)
        namespace: dict[str, Any] = mix.NameSpace.prepare1(extras=extras)
        new_cls = type(cls_name, self.vault.mixins, namespace)
        return cast(MixT, new_cls)

    def inject[TargeT: type](
        self, cls: type, prepend: bool = True, extras: dict | None = None
    ) -> TargeT:
        """Inject the registry's mixins into an existing cls class."""
        # Mixins go before the cls for overrides, after for fallbacks

        bases: tuple[type, ...] = (
            self.vault.mixins + (cls,)
            if prepend
            else (cls,) + self.vault.mixins
        )

        cls_name: str = self._generate_name(cls=cls)
        namespace: dict[str, Any] = mix.NameSpace.prepare1(cls, extras)
        new_cls = type(cls_name, bases, namespace)

        return cast(typ=TargeT, val=new_cls)

    # TODO: overload
    def mix[TargeT: type](
        self, cls: TargeT | None = None, **kwargs: Any
    ) -> TargeT | MixT:
        """Dispatch to build or inject based on input."""
        if cls is None:
            return self.build(**kwargs)
        return self.inject(cls, **kwargs)
