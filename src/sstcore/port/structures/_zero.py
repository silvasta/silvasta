"""
Utils

-
"""

__all__: list[str] = [
    "LoaderView",
]

import typing as _typing
from typing import ClassVar

from ..empty import VOID, Ghost

if _typing.TYPE_CHECKING:
    from ._loader import Loader

    _LoaderViewBase = Loader
else:
    _LoaderViewBase = Ghost


def _rich_colorize(target, color="bold cyan", /):
    return f"[{color}]{target}[/]" if color else target


_c = _rich_colorize


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


if _typing.TYPE_CHECKING:

    class LoaderView: ...
else:
    LoaderView = _LoaderView
