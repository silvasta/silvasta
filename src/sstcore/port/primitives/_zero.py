"""
Utils

-
"""

__all__: list[str] = [
    "portlink1",
    "unpack_types",
    "get_slots",
    "iter_slot_names",
    "stringed",
    "uniqued",
    "is_notext_sequence",
    # views
    "NameView",
]

import collections.abc as _cabc
import typing as _typing
from collections.abc import Callable
from functools import cache
from types import UnionType
from typing import ClassVar, Union

from .._types import Types as _T  # noqa:N814


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


def is_notext_sequence(target: object, /) -> bool:
    # RENAME:
    # LATER: any idea how to subtract StrLike from Sequence in TypeGuard?
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
