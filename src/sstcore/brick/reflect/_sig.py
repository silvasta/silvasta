"""
Callable Signature Inspection

-
"""

__all__: list[str] = [
    "find",
    "types",
    "params",
    "returns",
    "Binding",
    "is_async",
    "is_generator",
]

import enum as _e
import inspect as _inspect
from collections.abc import Callable
from collections.abc import Callable as _Callable
from typing import Any as _Any

from ...port._types import Types as _T  # noqa:N814  # noqa:N814
from ...port.empty import VOID as _VOID
from ...port.empty import MayNot as _MayNot
from ...port.solid import EnumZero
from . import _typehint


def is_async(call: _Callable, /, *, unwrap=False):
    return _inspect.iscoroutinefunction(
        _unwrapped := _inspect.unwrap(call) if unwrap else call
    ) or _inspect.isasyncgenfunction(_unwrapped)


def is_generator(call: _Callable, /, *, unwrap=False):
    return _inspect.isgeneratorfunction(
        _unwrapped := _inspect.unwrap(call) if unwrap else call
    ) or _inspect.isasyncgenfunction(_unwrapped)


def _resolve_routine(call: _Callable, /, *, unwrap: bool = False) -> _Callable:
    target: _Callable = (
        call.__call__
        if callable(call)
        and not isinstance(call, type)
        and not _inspect.isroutine(call)
        else call
    )
    return _inspect.unwrap(target) if unwrap else target


class Binding(EnumZero):
    FUNC = _e.auto()
    METHOD = _e.auto()
    CLASS = _e.auto()
    STATIC = _e.auto()

    @classmethod
    def detect(cls, target: Callable, /) -> Binding:
        match target:
            case staticmethod():
                return cls.STATIC
            case classmethod():
                return cls.CLASS
            case _ if getattr(target, "__self__", None) is not None:
                return cls.METHOD
            case _:
                return cls.FUNC

    def raw(self, target: Callable, /) -> Callable:
        return target.__func__ if self in {self.CLASS, self.STATIC} else target  # ty:ignore


def find(func: _Callable, /) -> _MayNot[_inspect.Signature]:
    try:
        return _inspect.signature(func)
    except TypeError, ValueError:
        return None


def types(func: _Callable[..., _Any]) -> tuple[_Any, _Any]:
    """Extract Params and Result of Callable[**P, R]"""

    sig: _MayNot[_inspect.Signature] = find(func)

    if sig is None:
        return _VOID, _VOID

    hints: _MayNot[_T.StrDict] = _typehint.find(func)
    returned: _Any = returns(hints, sig)
    sig_params: list[_Any] = params(hints, sig)

    return tuple(sig_params), returned


def params(hints: _MayNot[_T.StrDict], sig: _inspect.Signature) -> list[_Any]:
    return [
        hints[name]
        if hints is not None and name in hints
        else param.annotation
        if param.annotation is not _inspect.Signature.empty
        else _Any
        for name, param in sig.parameters.items()
    ]


def returns(hints: _MayNot[_T.StrDict], sig: _inspect.Signature) -> _Any:
    return (
        hints["return"]
        if hints is not None and "return" in hints
        else (
            _VOID
            if (returned := sig.return_annotation) is _inspect.Signature.empty
            else returned
        )
    )
