"""
Prepare, Hold and Distribute the Mixins (and Protocols)

-
"""

__all__: list[str] = [
    "MixinRegistry",
    "DuoRegistry",
]

from typing import TYPE_CHECKING, Any, Literal, NoReturn

from ....port.register import MixinRegister
from ...registry import TupleRegistry


class MixinRegistry[MixinT: type](TupleRegistry[MixinT]):
    """Gatekeeper for mixin order. Assembly stays in brick.mix / the composer."""

    def _guard_input(self, item: type | Any) -> None | NoReturn:
        if isinstance(item, type):
            return
        raise TypeError("MixinRegistry only accepts classes", item)

    @property
    def mixins(self) -> tuple[type, ...]:
        return self.items


class DuoRegistry[DuoT: tuple[type, type]](TupleRegistry[DuoT]):
    """Hold Mixins and Protocols in Paralell"""

    # NEXT:
    def _guard_input(self, item: DuoT | Any) -> None | NoReturn:
        if isinstance(item[0], type) and isinstance(item[1], type):
            return
        raise TypeError("MixinRegistry only accepts classes", item)

    def _split(self, *, mixin_or_protocol: Literal[0, 1]) -> tuple[type, ...]:
        return tuple(duo[mixin_or_protocol] for duo in self.items)

    @property
    def mixins(self) -> tuple[type, ...]:
        return self._split(mixin_or_protocol=0)

    @property
    def protocols(self) -> tuple[type, ...]:
        return self._split(mixin_or_protocol=1)


# NEXT:
# NEXT:
# NEXT:
# NEXT:
if TYPE_CHECKING:
    _instance: MixinRegister = MixinRegistry()
    _class: type[MixinRegister] = MixinRegistry
    #
    _instance: MixinRegister = DuoRegistry()
    _class: type[MixinRegister] = DuoRegistry
