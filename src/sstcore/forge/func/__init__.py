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
    "ArgCast",
    "ArgCaster",
]
from ._cast import ArgCast, ArgCaster
from ._tor import BaseFunctor, HybridFunctor, SafeFunctor
