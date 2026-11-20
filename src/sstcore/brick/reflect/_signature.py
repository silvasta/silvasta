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

from sstcore.port.empty import VOID


def looks_generic(target: Any) -> bool:
    """True if target or any class in its MRO declares type parameters or generic bases."""
    if (
        not isinstance(target, type)
        and getattr(target, "__orig_class__", None) is not None
    ):
        return True
    cls = target if isinstance(target, type) else type(target)
    for klass in cls.__mro__:
        if getattr(klass, "__type_params__", ()):
            return True
        if getattr(klass, "__orig_bases__", ()):
            return True
    return False


def extract_signature_types(func: Callable[..., Any]) -> tuple[Any, Any]:
    """``(parameter types, return type)`` from annotations and resolved type hints.

    Failure of either ``signature`` or ``get_type_hints`` degrades that
    side to VOID or to the raw annotation.
    """
    try:
        sig = signature(func)
    except TypeError, ValueError:
        return VOID, VOID

    hints: dict[str, Any] | None
    try:
        hints = _t.get_type_hints(func)
    except NameError, TypeError, ValueError:
        hints = None

    if hints is not None and "return" in hints:
        returned: Any = hints["return"]
    else:
        returned = sig.return_annotation
        if returned is Signature.empty:
            returned = VOID

    parameters: list[Any] = []
    for name, param in sig.parameters.items():
        if hints is not None and name in hints:
            parameters.append(hints[name])
        elif param.annotation is not Signature.empty:
            parameters.append(param.annotation)
        else:
            parameters.append(Any)
    return tuple(parameters), returned
