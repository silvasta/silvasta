"""
brick.call

- Callable Fragments
- Func input ensured
                                                        reflect(+1)
                              DependencyLevel.sstcore.brick.call[1]
"""

__all__: list[str] = [
    "just_return",
    "validate_signature",
    #
    "ArgCast",
    "ArgCaster",
    "ArgCasting",
    "CastInput",
    "castarg",
    #
    "SigVar",
    "SigSpec",
]

from ._argcast import ArgCast, ArgCaster, ArgCasting, CastInput
from ._inspect import validate_signature
from ._signature import SigSpec, SigVar
from ._some import just_return

castarg = ArgCast()  # TARGET: Main Result of ArgCast
