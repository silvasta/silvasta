"""
forge.func

- Closures with Comfort
- Func input ensured

"""

__all__: list[str] = [
    "BaseFunctor",
    "SafeFunctor",
    "HybridFunctor",
    #
    "ArgCaster",
    "ArgCast",
    "castarg",
]
from ._cast import ArgCast, ArgCaster, castarg
from ._tor import BaseFunctor, HybridFunctor, SafeFunctor
