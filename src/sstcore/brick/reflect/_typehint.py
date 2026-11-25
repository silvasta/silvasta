"""
Type Hint Detection

-
"""

__all__: list[str] = [
    "find",
    "iter",
    "unwrap_alias",
]

import inspect as _inspect
import typing as _t
from collections.abc import Callable as _Callable
from types import UnionType as _UnionType

from ...port._types import CallingTypes as _CT  # noqa: N814
from ...port._types import Types as _T  # noqa:N814

# TODO: check port.primitives._zero.unpack_types


def find(func: _Callable, /, include_extras: bool = True) -> _T.StrDict:
    """Extract TypeHints from any Callable or get empty dict"""
    target: _t.Any = (
        func.__call__
        if callable(func)
        and not isinstance(func, type)
        and not _inspect.isroutine(func)
        else func
    )
    try:
        return _t.get_type_hints(target, include_extras=include_extras)
    except NameError, TypeError, ValueError:
        return getattr(target, "__annotations__", {})


def iter(target: _CT.Castable, /) -> _t.Iterator[tuple[str, _t.Any]]:
    # LATER:: check _CT:Castable
    """Provide TypeHint with fully unpacked and iterated TypedDicts"""
    for name, hint in unwrap_alias(target):
        if _t.get_origin(hint) is _t.Unpack:
            _unpacked_typed_dict = _t.get_args(hint)[0]
            yield name, _unpacked_typed_dict
            yield from iter(_unpacked_typed_dict)
        else:
            yield name, hint


def unpack_union(target: object, /) -> tuple[_t.Any, ...]:
    while isinstance(target, _t.TypeAliasType):
        target = target.__value__
    origin: _t.Any | None = _t.get_origin(target)
    if origin is _t.Union or origin is _UnionType:
        return _t.get_args(target)
    return (target,)


def unwrap_alias(target: _CT.Castable, /) -> _t.Iterator[tuple[str, _t.Any]]:
    """Unwrap (Generic-) Aliases, like: Input[Args, Result] -> Input"""
    _origin = _t.get_origin(target) or target
    for name, hint in _t.get_type_hints(_origin, include_extras=True).items():
        if name == "return":
            continue
        while isinstance(hint, _t.TypeAliasType):
            hint: _t.Any = hint.__value__
        yield name, hint
