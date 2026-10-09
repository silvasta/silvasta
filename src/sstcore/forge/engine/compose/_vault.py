"""
Prepare, Hold and Distribute the Mixins (and Protocols)

-
"""

__all__: list[str] = [
    "MixinRegistry",
    "DuoRegistry",
]

from typing import Any, Literal, NoReturn

from ....brick.vault import TupleVault
from ....port.link import portlink
from ....port.register import MixinRegister

# NEXT: build solid stack


@portlink(MixinRegister)
class MixinRegistry[MixinT: type](TupleVault[MixinT]):
    """Gatekeeper for mixin order. Assembly stays in brick.mix / the composer."""

    def _guard_input(self, item: type | Any) -> None | NoReturn:
        if isinstance(item, type):
            return
        raise TypeError("MixinRegistry only accepts classes", item)

    @property
    def mixins(self) -> tuple[type, ...]:
        return self.vault


@portlink(MixinRegister)
class DuoRegistry[DuoT: tuple[type, type]](TupleVault[DuoT]):
    """Hold Mixins and Protocols in Paralell"""

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
