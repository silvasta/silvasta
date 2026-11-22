"""
Utils

-
"""

__all__: list[str] = [
    "unpack_types",
    "NameView",
    "portlink1",
]

import typing as _typing
from collections.abc import Callable
from functools import cache
from types import UnionType
from typing import TYPE_CHECKING, ClassVar, TypeAliasType, Union

from ..empty import VOID, Ghost


def portlink1[C, P](_protocol: type[P], /) -> Callable[[type[C & P]], type[C]]:  # ty:ignore
    """Anchor an Implementation to its Protocol - How everything began..."""

    def wrapper(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
        """Accept class C iff C implements P and return C unchanged"""

        return cls

    return wrapper


@cache
def unpack_types(target: object, /) -> tuple[type, ...]:
    """Flatten TypeAliases or UnionTypes into runtime-checkable Classes"""

    if isinstance(target, TypeAliasType):
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


def _rich_colorize(target, color="bold cyan", /):
    return f"[{color}]{target}[/]" if color else target


_c = _rich_colorize


class NameView:
    pattern: str
    keys: tuple[str, ...]

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


if TYPE_CHECKING:
    from ._loader import Loader

    _LoaderViewBase = Loader
else:

    class _LoaderViewBase(Ghost): ...


class _LoaderView(_LoaderViewBase):
    _color: ClassVar[str] = "b steel_blue1"

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, color: str, /) -> None:
        type(self)._color = color

    def __str__(self) -> str:
        name: str = type(self).__name__
        is_ready: str = "👍️" if self.is_ready else "👎️"
        _in, _out = self.type_args.sig()
        _typearg = f"{_in} -> {_out}"
        _source = self.type_args.parameters_source
        return f"{name}[{is_ready}({self._value}) | {_typearg} via {_source}]"

    def __repr__(self) -> str:
        _d = {
            "func": getattr(self._func, "__name__", repr(self._func)),
            "default": repr(self._default),
            "prefer": self._prefer,
            "counter": f"{self._counter}/{self._total_counter}",
            "type_args": self.type_args,
        }
        return f"{self}({', '.join(f'{k}={v}' for k, v in _d.items())})"

    def __rich__(self) -> str:
        _orange = "orange_red1"
        _name = _c(type(self).__name__, self.color)
        _is_ready = _c("👍️", "green") if self.is_ready else _c("👎️", _orange)
        _value = _c(self._value, _orange if self._value is VOID else "cyan")
        _in, _out = self.type_args.sig()
        _typearg = f"{_c(_in, 'steel_blue1')} -> {_c(_out, 'green')}"
        _source = _c(self.type_args.parameters_source, "steel_blue1")
        return f"{_name}[{_is_ready}({_value}) | {_typearg} via {_source}]"


if TYPE_CHECKING:

    class LoaderView: ...
else:
    LoaderView = _LoaderView
