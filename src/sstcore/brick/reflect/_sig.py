"""
Callable Signature Inspection

-
"""

__all__: list[str] = [
    "types",
    "find",
    "params",
    "returns",
]

import inspect as _i
from collections.abc import Callable as _Callable
from typing import Any

from ...port._types import Types as _T  # noqa:N814
from ...port.empty import VOID as _VOID
from ...port.empty import MayNot as _MayNot
from . import _typehint


def find(func: _Callable, /) -> _MayNot[_i.Signature]:
    # NEXT: StrategyField: func, bind_to_self=self.bind_to_self
    try:
        return _i.signature(func)
    except TypeError, ValueError:
        return None


def types(func: _Callable[..., Any]) -> tuple[Any, Any]:
    """Extract Params and Result of Callable[**P, R]"""

    sig: _MayNot[_i.Signature] = find(func)

    if sig is None:
        return _VOID, _VOID

    hints: _MayNot[_T.StrDict] = _typehint.find(func)
    returned: Any = returns(hints, sig)
    sig_params: list[Any] = params(hints, sig)

    return tuple(sig_params), returned


def params(hints: _MayNot[_T.StrDict], sig: _i.Signature) -> list[Any]:
    # CHECK: use the tuple?
    return [
        hints[name]
        if hints is not None and name in hints
        else param.annotation
        if param.annotation is not _i.Signature.empty
        else Any
        for name, param in sig.parameters.items()
    ]


def returns(hints: _MayNot[_T.StrDict], sig: _i.Signature) -> Any:
    return (
        hints["return"]
        if hints is not None and "return" in hints
        else (
            _VOID
            if (returned := sig.return_annotation) is _i.Signature.empty
            else returned
        )
    )
