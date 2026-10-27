"""
Prepare, Hold and Distribute the Mixins (and Protocols)

-
"""

__all__: list[str] = [
    "MixinRegistry",
    "DuoRegistry",
]

from typing import Any, Literal

from ...brick.color import colorize
from ...brick.vault import TupleVault
from ...port.link import portlink
from ...port.register import MixinRegister


@portlink(MixinRegister)
class MixinRegistry[MixinT: type](TupleVault[MixinT]):
    """Gatekeeper for mixin order. Assembly stays in brick.mix / the composer."""

    def _normalize(self, value: Any) -> MixinT:
        if isinstance(value, type):
            return super()._normalize(value)
        raise TypeError("MixinRegistry only accepts classes", value)

    @property
    def mixins(self) -> tuple[type, ...]:
        return self.vault

    def display(self) -> str:
        """Show all selected Mixins colorized in Order"""
        mixins: str = "\n".join(colorize.modules(m) for m in self.mixins)
        # IDEA: Console().print(mixins)
        return mixins


@portlink(MixinRegister)
class DuoRegistry[DuoT: tuple[type, type]](TupleVault[DuoT]):
    """Hold Mixins and Protocols in Parallel"""

    def _normalize(self, value: Any) -> DuoT:
        if isinstance(value[0], type) and isinstance(value[1], type):
            return super()._normalize(value)
        raise TypeError("MixinRegistry only accepts classes", value)

    def _split(self, *, mixin_or_protocol: Literal[0, 1]) -> tuple[type, ...]:
        return tuple(duo[mixin_or_protocol] for duo in self.vault)

    @property
    def mixins(self) -> tuple[type, ...]:
        return self._split(mixin_or_protocol=0)

    @property
    def protocols(self) -> tuple[type, ...]:
        return self._split(mixin_or_protocol=1)
