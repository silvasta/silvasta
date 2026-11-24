"""
Type Hint Detection

-
"""

__all__: list[str] = [
    "find",
    "iter",
    "unwrap",
]
import typing as _t
from collections.abc import Callable as _Callable

from ...port._types import CallingTypes as _CT  # noqa: N814
from ...port._types import Types as _T  # noqa:N814
from ...port.empty import MayNot as _MayNot

# TODO: check port.primitives._zero.unpack_types


def find(func: _Callable, /) -> _MayNot[_T.StrDict]:
    try:
        return _t.get_type_hints(func)
    except NameError, TypeError, ValueError:
        return None


def iter(target: _CT.Castable, /) -> _t.Iterator[tuple[str, _t.Any]]:
    """Provide TypeHint with fully unpacked and iterated TypedDicts"""

    for name, hint in unwrap(target):
        if _t.get_origin(hint) is _t.Unpack:
            _unpacked_typed_dict = _t.get_args(hint)[0]
            yield name, _unpacked_typed_dict
            yield from iter(_unpacked_typed_dict)
        else:
            yield name, hint


# TODO: check _CT:Castable


def unwrap(target: _CT.Castable, /) -> _t.Iterator[tuple[str, _t.Any]]:
    """Unwrap (Generic-) Aliases, like: Input[Args, Result] -> Input"""
    _origin = _t.get_origin(target) or target
    for name, hint in _t.get_type_hints(_origin, include_extras=True).items():
        if name == "return":
            continue
        while isinstance(hint, _t.TypeAliasType):
            hint: _t.Any = hint.__value__
        yield name, hint
