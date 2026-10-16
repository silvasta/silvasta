"""
forge.func

- Closures with Comfort
- Func input ensured

"""

__all__: list[str] = [
    "BaseFunctor",
    "SafeFunctor",
    "HybridFunctor",
]


from ._hybrid import HybridFunctor
from ._safe import SafeFunctor
from ._tor import BaseFunctor
