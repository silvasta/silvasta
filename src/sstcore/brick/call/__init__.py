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
    "castarg",
]

from ._argcast import ArgCast, ArgCaster, castarg
from ._inspect import validate_signature
from ._some import just_return


# IDEA: make each item a Rule:
# - each Rule has a name, a field in Spec and Input and a resolver
# - maybe even as some IntFlag that can be switched fast
