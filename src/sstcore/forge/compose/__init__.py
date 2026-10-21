"""
Class Composition - Assemble the Layouts for Instances

- NEXT, complete and somewhen find own file, latest when second topic arrives

"""

__all__: list[str] = [
    # vault
    "MixinRegistry",
    "DuoRegistry",
    # assembler
    "MixinBuilder",
    "MixInjector",
]

from ._builder import MixinBuilder
from ._injector import MixInjector
from ._vault import DuoRegistry, MixinRegistry
