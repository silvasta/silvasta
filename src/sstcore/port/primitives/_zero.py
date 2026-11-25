"""
Utils

-
"""

__all__: list[str] = [
    "UnitField",
    "unpack_types",
    "get_slots",
    "iter_slot_names",
    "stringed",
    "uniqued",
    "is_notext_iter",
    "NameView",
    "portlink1",
]

import collections.abc as _cabc
import typing as _typing
from collections.abc import Callable
from functools import cache
from types import UnionType
from typing import Any, ClassVar, Self, Union, overload

from .._types import Types as _T  # noqa:N814
from ..empty import VOID, MayBe, MayNot


def portlink1[C, P](_protocol: type[P], /) -> Callable[[type[C & P]], type[C]]:  # ty:ignore
    """Anchor an Implementation to its Protocol - How everything began..."""

    def wrapper(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
        """Accept class C iff C implements P and return C unchanged"""

        return cls

    return wrapper


@cache
def unpack_types(target: object, /) -> _T.Tuple[type]:
    """Flatten TypeAliases or UnionTypes into runtime-checkable Classes"""

    if isinstance(target, _typing.TypeAliasType):
        return unpack_types(target.__value__)

    if isinstance(target, UnionType) or _typing.get_origin(target) is Union:
        return tuple(
            cls
            for member in _typing.get_args(target)
            for cls in unpack_types(member)
        )
    if isinstance(target, _typing.TypeVar):
        return unpack_types(
            target.__default__
            if target.__default__ is not _typing.NoDefault
            else target.__bound__
        )
    if isinstance(resolved := _typing.get_origin(target) or target, type):
        return (resolved,)

    raise TypeError(f"Cannot unpack runtime type from {target!r}")


def get_slots(cls: type) -> _cabc.Iterable[str]:
    _slots = cls.__dict__.get("__slots__", ())
    return _slots if not isinstance(_slots, str) else (_slots,)


def iter_slot_names(target: object) -> _cabc.Iterable[str]:
    seen: set[str] = set()
    for cls in type(target).__mro__:
        for slot in get_slots(cls):
            if slot in ("__dict__", "__weakref__"):
                continue
            if slot.startswith("__") and not slot.endswith("__"):
                slot = f"_{cls.__name__.lstrip('_')}{slot}"
            if slot not in seen and hasattr(target, slot):
                seen.add(slot)
                yield slot


def uniqued(name: str, out: _T.StrDict | set[str]):
    """Increment Dict Key Suffix until it is Unique"""
    key: str = name
    counter = 1
    while key in out:
        key = f"{name}_{counter}"
        counter += 1
    return key


def is_notext_iter(target: object, /) -> bool:
    return isinstance(target, _cabc.Sequence) and not (
        isinstance(target, (str, bytes, bytearray))
    )


def stringed(val: object, /, *, verbose: bool = False) -> str:
    """Format values cleanly (types and functions by name unless verbose)"""
    if verbose:
        return repr(val)
    if isinstance(val, type):
        return val.__name__
    if callable(val) and hasattr(val, "__name__"):
        return getattr(val, "__qualname__", getattr(val, "__name__", repr(val)))
    return str(val)


#  LINE: -- Views -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _rich_colorize(target, color="bold cyan", /):
    return f"[{color}]{target}[/]" if color else target


class NameView:
    pattern: str
    keys: _T.Tuple[str]

    _color: ClassVar[str] = "cyan"

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, color: str, /) -> None:
        type(self)._color = color

    @property
    def _short(self) -> str:
        return f"{len(self.keys)}:"

    def __str__(self):
        return f"{type(self).__name__}[{self._short}]"

    def __repr__(self):
        _name = s[0:-1] if (s := f"{self}").endswith("]") else ""
        _keys = ", ".join(self.keys)
        return f"{_name} | '{self.pattern}' -> {{{_keys}}}]"

    def __rich__(self):
        """Final goal: all keys in pattern same color as extracted"""
        _name = _rich_colorize(type(self).__name__, self.color)
        _keys = ", ".join(_rich_colorize(k, self.color) for k in self.keys)
        return f"{_name}[{self._short} | '{self.pattern}' -> {{{_keys}}}]"


#  LINE: -- Field -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class UnitField[Value]:
    """Cache Data per Instance by unit.__dict__"""

    def __init__(self, default: MayBe[Value], /):
        self._default: MayBe[Value] = default

    @overload
    def __get__(self, unit: None, caller: type) -> Self: ...
    @overload
    def __get__(self, unit: object, caller: type) -> Value: ...
    def __get__(self, unit: MayNot, _caller: type) -> Self | Value:
        """Extract per Unit from Cache or try set Default"""
        return self if unit is None else self[unit]

    def __set__(self, unit: object, value: Value) -> None:
        """Update the per Instance Cache with the Value"""
        self[unit] = value

    def __set_name__(self, host: type, name: str) -> None:
        """Define the Name, Assigner:{initial owner} and Hoster:{last owner}"""
        self._name: str = name
        self._host: type = host

    def __contains__(self, target: object):
        """Heavily Wired! Change with care..."""
        return self._name in vars(target)

    def __getitem__(self, unit: object):
        if unit not in self:
            self[unit] = self._default
        return vars(unit)[self._name]

    def __setitem__(self, unit: object, value: Any):
        if value is VOID:
            raise RuntimeError(f"Assign Value or Default to Access: {self}")
        vars(unit)[self._name] = value

    def __delete__(self, unit: object) -> None:
        """Remove the Value of Unit from the Cache"""
        vars(unit).pop(self._name, None)

    def __str__(self):
        """Represent (HostCls::)Cls.field_name"""
        caller: type = type(self)
        scope: str = f"::{caller.__name__}" if caller is not self._host else ""
        return f"{self._host.__name__}{scope}.{self._name}"

    def __call__[Fn: Callable](self, func: Fn) -> Fn:
        """Make a Method Exchangeable"""
        self._default: Fn = func
        return func
