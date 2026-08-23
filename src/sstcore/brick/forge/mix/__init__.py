"""
Class Composition - Assemble the Layouts for Instances

- NEXT

"""

from typing import TYPE_CHECKING

__all__: list[str] = [
    "combine_mixins",
    "MixinRegistry",
]

from ....port.register import MixinRegister


# LATER: this as 1 out of n options to select
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


# NEXT:
class MixinRegistry: ...


if TYPE_CHECKING:
    _instance: MixinRegister
    _class: type[MixinRegister]
