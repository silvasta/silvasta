"""
Most basic parts

- Keep Attr Definition
- Assign general methods and dunders

"""

__all__: list[str] = [
    "NamedValue",
    "SingleTuple",
]

import builtins as _b
import collections.abc as _cabc
import typing as _typing
from inspect import _ParameterKind
from typing import Any

from .. import empty as _empty
from ._format import format_named_value
from ._hashed import HashedTuple
from ._tuplebase import get_named_value_item

#  LINE: -- Pure Definitions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _NamedValue[T: Any = Any](_typing.NamedTuple):
    name: str
    value: T


class _SigVar(_typing.NamedTuple):
    name: str
    kind: _ParameterKind
    default: Any = _empty.VOID
    annotation: Any = _empty.VOID


class _SingleTuple[T: Any = Any](_typing.NamedTuple):
    data: T


class _Variadics[
    A: SingleTuple[Any] = SingleTuple[Any],
    K: SingleTuple[Any] = SingleTuple[Any],
](_typing.NamedTuple):
    args: A
    kwargs: K


class _ExplainBase[T: Any = Any](_typing.NamedTuple):
    origin: T
    title: str
    detail: str = ""


#  LINE: -- Default Methods -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class NamedValue[T: Any = Any](_NamedValue[T]):
    """Define the Handling and Visualization of the Name and Value"""

    def __bool__(self) -> bool:
        return bool(self.value)

    def __format__(self, spec: str) -> str:
        return format_named_value(self, spec)

    def __getitem__(self, key: str | int) -> T | str:  # ty: ignore
        """Hardcore Encode Default Behaviour plus Var()[name]=value access"""
        return get_named_value_item(self, key)

    def keys(self) -> _cabc.KeysView[str]:
        return _cabc.KeysView({self.name: None})

    def hashed(self, strict: bool = True) -> HashedTuple:
        """Recursively Enforce Freeze and Hash (strict=False -> str(obj))"""
        return HashedTuple(*self, strict=strict)


class SingleTuple[T: Any = Any](_SingleTuple[T]):
    """Define the Forwarding of the Single Data Point"""

    def __iter__(self) -> _cabc.Iterator:
        yield from self.data

    def __len__(self) -> int:  # ty:ignore
        return len(self.data)

    def __bool__(self) -> bool:
        return bool(self.data)

    def __contains__(self, item: object) -> bool:
        return item in self.data

    @property
    def tuple(self) -> _b.tuple[T]:
        return _b.tuple(self.data)

    @property
    def list(self) -> _b.list[T]:
        return _b.list(self.data)

    @property
    def set(self) -> _b.set[T]:
        return _b.set(self.data) if HashedTuple.accepts(self.data) else set()
