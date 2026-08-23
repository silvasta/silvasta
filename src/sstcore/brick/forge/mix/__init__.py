"""
Class Composition - Assemble the Layouts for Instances

- NEXT, complete and somewhen find own file, latest when second topic arrives

"""

from typing import TYPE_CHECKING, Any, NoReturn, cast

__all__: list[str] = [
    "combine_mixins",
    "MixinRegistry",
]

from ....port.register import MixinRegister
from ...registry import TupleRegistry


# LATER: this as 1 out of multiple sort options
def combine_mixins(
    registered: tuple[type, ...],
    extra: tuple[type, ...],
    *,
    prepend: bool = True,
) -> tuple[type, ...]:
    """Place ephemeral mixins before (override) or after (fallback) the recipe"""
    if not extra:
        return registered
    return extra + registered if prepend else registered + extra


# AI_QUESTION: so far I am quite sure the registry below replaces half the composer
# - For sure the entire coordination and selection of mixins comes from Composer
# - Here Maximum to a level where it builds or injects a class
# - where to set the border in between Registry/Assembler?
class MixinRegistry[MixinT: type](TupleRegistry[type]):
    """Gatekeeper for mixin order. Assembly stays in brick.mix / the composer."""

    def _guard(self, item: type | Any) -> None | NoReturn:
        if isinstance(item, type):
            return
        raise TypeError("MixinRegistry only accepts classes", item)

    @property
    def mixins(self) -> tuple[type, ...]:
        return self.items

    def build(self, *_args, extras=None, **_kwargs) -> MixinT:
        new_cls: type = type("MyClass", self.mixins, extras or {})
        return cast(typ=MixinT, val=new_cls)

    # AI: here with the Parameter, directly cast, use this here or adapt in Composer
    def inject[TargeT: type](self, *_args, extras=None, **_kwargs) -> TargeT:
        new_cls: type = type("MyClass", self.mixins, extras or {})
        return cast(typ=TargeT, val=new_cls)


if TYPE_CHECKING:
    _instance: MixinRegister = MixinRegistry()
    _class: type[MixinRegister] = MixinRegistry
