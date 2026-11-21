"""
Utils

-
"""

from collections.abc import Callable


def _portlink1[C, P](_protocol: type[P], /) -> Callable[[type[C & P]], type[C]]:  # ty:ignore
    """Anchor an Implementation to its Protocol"""

    def wrapper(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
        """Accept class C iff C implements P and return C unchanged"""

        return cls

    return wrapper


class NameView:
    pattern: str
    keys: tuple[str, ...]

    @property
    def _color(self):  # NEXT: field!?
        return "cyan"

    def __str__(self):
        return f"{_clsname(self)}[{_keys(self)}]"

    def __repr__(self):
        return f"{self}[{_keys(self)}::'{self.pattern}']"

    def __rich__(self):
        _c = self._color
        _name = _color(_clsname(self), _c)
        return f"{_name}[{_short(self)}][{_keys(self, _c)}::'{self.pattern}']"


def _clsname(self):
    return type(self).__name__


def _short(self):
    return f"{len(self.keys)}:"


def _color(target, color="cyan", /):
    return f"[{color}]{target}[/]" if color else target


def _keys(self, color=None, /):
    return ":".join(_color(k, color) for k in self.keys)
