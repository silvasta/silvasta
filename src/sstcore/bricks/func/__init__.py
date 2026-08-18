"""
The Functor - Easy and Safe Binding!

- Closures with Comfort

"""

__all__: list[str] = [
    "Functor",
    "SafeFunctor",
    "DecoFunctor",
]

from ._base import DecoFuncMixin, FunctorCore, SafeFuncMixin


class Functor[**P, R](
    DecoFuncMixin[P, R], SafeFuncMixin[P, R], FunctorCore[P, R]
): ...


class SafeFunctor[**P, R](DecoFuncMixin[P, R], FunctorCore[P, R]): ...


class DecoFunctor[**P, R](DecoFuncMixin[P, R], FunctorCore[P, R]): ...
