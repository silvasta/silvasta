"""
Type Detection

-
"""

__all__: list[str] = [
    "overlap",
    "is_untyped",
    "is_subtype",
]

import inspect as _inspect
import typing as _t

from ...port.empty import VOID
from . import _typehint

_EMPTY = _inspect._empty


def overlap(target1: object, target2: object, /) -> bool:
    if is_untyped(target1) or is_untyped(target2):
        return True
    return any(
        is_subtype(a, b) or is_subtype(b, a)
        for a in _typehint.unpack_union(target1)
        for b in _typehint.unpack_union(target2)
    )


def _strip_wrapper(tp: _t.Any) -> _t.Any:
    while isinstance(tp, _t.TypeAliasType):
        tp = tp.__value__
    if _t.get_origin(tp) is _t.Annotated:
        tp = _t.get_args(tp)[0]
    return tp


def is_untyped(target: object, /) -> bool:
    return target is _t.Any or target is VOID or target is _EMPTY


def is_subtype(sub: _t.Any, sup: _t.Any, /) -> bool:
    """Best-effort runtime subtype check supporting unions, None, and generics."""

    sub: _t.Any = _strip_wrapper(sub)
    sup: _t.Any = _strip_wrapper(sup)

    if sub == sup or is_untyped(sup):
        return True
    if is_untyped(sub):
        return False
    if sub is None:
        sub: type[None] = type(None)
    if sup is None:
        sup: type[None] = type(None)

    sub_members: tuple[_t.Any, ...] = _typehint.unpack_union(sub)
    sup_members: tuple[_t.Any, ...] = _typehint.unpack_union(sup)

    if len(sub_members) > 1 or len(sup_members) > 1:
        return all(
            any(is_subtype(s_m, p_m) for p_m in sup_members)
            for s_m in sub_members
        )

    sub_origin: object = _t.get_origin(sub) or sub
    sup_origin: object = _t.get_origin(sup) or sup

    if isinstance(sub_origin, type) and isinstance(sup_origin, type):
        try:
            if not issubclass(sub_origin, sup_origin):
                return False
        except TypeError:
            return False

        if not (sup_args := _t.get_args(sup)):
            return True

        sub_args: tuple[_t.Any, ...] = _t.get_args(sub)
        if not sub_args:
            return False

        if (
            sup_origin is tuple
            and len(sup_args) == 2
            and sup_args[1] is Ellipsis
        ):
            if len(sub_args) == 2 and sub_args[1] is Ellipsis:
                return is_subtype(sub_args[0], sup_args[0])
            return all(is_subtype(sa, sup_args[0]) for sa in sub_args)

        if len(sub_args) != len(sup_args):
            return False

        return all(
            is_subtype(sa, pa)
            for sa, pa in zip(sub_args, sup_args, strict=True)
        )
    return False
