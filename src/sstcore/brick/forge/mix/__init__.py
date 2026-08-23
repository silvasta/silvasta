"""
Class Composition - Assemble the Layouts for Instances

- NEXT, complete and somewhen find own file, latest when second topic arrives

"""

__all__: list[str] = [
    "mix",
    # vault
    "MixinRegistry",
    "DuoRegistry",
    # assembler
    "MixinComposer",
    "MixInjector",
]

from . import _mixer as mix
from ._composer import MixinComposer
from ._injector import MixInjector
from ._vault import DuoRegistry, MixinRegistry
