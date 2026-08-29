"""
The Functor - Easy and Safe Binding!

- Closures with Comfort

"""

__all__: list[str] = [
    "Functor",
    "SafeFunctor",
    "DecoFunctor",
]

from ._base import BaseFunctor, DecoFuncMixin, SafeFuncMixin


class Functor[**P, R](
    DecoFuncMixin[P, R], SafeFuncMixin[P, R], BaseFunctor[P, R]
): ...


class SafeFunctor[**P, R](DecoFuncMixin[P, R], BaseFunctor[P, R]): ...


class DecoFunctor[**P, R](DecoFuncMixin[P, R], BaseFunctor[P, R]): ...
