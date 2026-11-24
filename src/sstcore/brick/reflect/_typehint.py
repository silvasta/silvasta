"""
Type Hint Detection

-
"""

__all__: list[str] = [
    "iter_type_hints",
    "unwrap_type_hints",
    "is_variadic",
]
import typing as _t
from typing import Any

from ...port._types import CallingTypes as _CT  # noqa: N814

type Variadic = _t.ParamSpec | _t.TypeVarTuple

# REMOVE: is now done by the func
VARIADICS: tuple[type, ...] = _t.get_args(Variadic.__value__)


def is_variadic(target: object, /) -> _t.TypeIs[Variadic]:
    # CHECK: generally variadic? maybe better name
    return isinstance(target, _t.get_args(Variadic.__value__))


def unwrap_type_hints(target: _CT.Castable, /) -> _t.Iterator[tuple[str, Any]]:
    """Unwrap (Generic-) Aliases, like: Input[Args, Result] -> Input"""
    _origin = _t.get_origin(target) or target
    for name, hint in _t.get_type_hints(_origin, include_extras=True).items():
        if name == "return":
            continue
        while isinstance(hint, _t.TypeAliasType):
            hint: Any = hint.__value__
        yield name, hint


def iter_type_hints(target: _CT.Castable, /) -> _t.Iterator[tuple[str, Any]]:
    # NEXT: NameHint tuple?
    # CHECK: combine with unpack_type? weave it in?
    """
    Yield (Name,Annotation) and TypedDicts recursively

    - provide full unpacked TypedDict plus iterate over its parts
    """

    for name, hint in unwrap_type_hints(target):
        if _t.get_origin(hint) is _t.Unpack:
            _unpacked_typed_dict = _t.get_args(hint)[0]
            yield name, _unpacked_typed_dict
            yield from iter_type_hints(_unpacked_typed_dict)
        else:
            yield name, hint
