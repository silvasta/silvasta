"""
Class Composition - Assemble the Layouts for Instances

- NEXT

"""

from typing import TYPE_CHECKING

__all__: list[str] = [
    "MixinRegistry",
]

# MOVE: to some separate file
from ....port.register import MixinRegister

if TYPE_CHECKING:
    _instance: MixinRegister
    _class: type[MixinRegister]
