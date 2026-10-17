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
    "ArgCasting",
    "castarg",
]

from ._cast import ArgCast, ArgCasting, castarg
from ._inspect import validate_signature
from ._some import just_return
