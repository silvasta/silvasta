"""
Callable Signature & Generic Presence Inspection

.
"""

__all__: list[str] = [
    "extract_signature_types",
    "looks_generic",
]

import typing as _t
from collections.abc import Callable
from inspect import Signature, signature
from typing import Any

from ...port._types import Types as _T  # noqa:N814
from ...port.empty import VOID, MayBe, MayNot


def type_instance(target: object) -> type:
    return target if isinstance(target, type) else type(target)


def looks_generic(target: Any) -> bool:
    """Any Target in the MRO declaring type parameters or generic bases?"""

    if not isinstance(target, type):
        return True
    if getattr(target, "__orig_class__", None) is not None:
        return True

    for _type in type_instance(target).__mro__:
        if getattr(_type, "__type_params__", ()):
            return True
        if getattr(_type, "__orig_bases__", ()):
            return True
    return False


def extract_signature_types(func: Callable[..., Any]) -> tuple[Any, Any]:
    # EXTRACT:
    # EXTRACT:
    # EXTRACT:
    # EXTRACT:
    """Extract Params and Result of Callable[**P, R]"""

    sig: MayBe[Signature] = _find_signature(func)

    if sig is VOID:
        return VOID, VOID

    hints: MayNot[_T.StrDict] = _find_type_hints(func)
    returned: Any = _extract_return_type(hints, sig)
    params: list[Any] = _extract_sig_params(hints, sig)

    return tuple(params), returned


def _extract_sig_params(hints: MayNot[_T.StrDict], sig: Signature) -> list[Any]:
    return [
        hints[name]
        if hints is not None and name in hints
        else param.annotation
        if param.annotation is not Signature.empty
        else Any
        for name, param in sig.parameters.items()
    ]


def _extract_return_type(hints: MayNot[_T.StrDict], sig: Signature) -> Any:
    return (
        hints["return"]
        if hints is not None and "return" in hints
        else (
            VOID
            if (returned := sig.return_annotation) is Signature.empty
            else returned
        )
    )


def _find_type_hints(func: Callable, /) -> MayNot[_T.StrDict]:
    try:
        return _t.get_type_hints(func)
    except NameError, TypeError, ValueError:
        return None


def _find_signature(func: Callable, /) -> MayBe[Signature]:  # EXTRACT:
    try:
        return signature(func)
    except TypeError, ValueError:
        return VOID
