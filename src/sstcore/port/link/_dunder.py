"""
Helper for Operators

- where to place later on?
"""

import typing as _t

from ..calling import Stringable


class DunderStore(_t.Protocol):
    def __init__(self, dunders: _t.Iterable[str] = ()): ...
    def get(self, name: str, *args, **kwargs) -> str | None: ...


class DunderFormat:
    @staticmethod
    def format(item: Stringable, /) -> str:
        return f"__{DunderFormat.extract(item)}__"

    @staticmethod
    def extract(item: Stringable, /) -> str:
        return str(item).strip("_")


class DunderDict(DunderFormat, dict):
    def __init__(self, dunders: _t.Iterable[str] = ()):
        for method in dunders:
            self[method] = None

    def __setitem__(self, key, _value=None):
        super().__setitem__(key.strip("_"), f"__{key.strip('_')}__")


class DunderSet(DunderFormat, frozenset):
    def __new__(cls, items: _t.Iterable[str] = (), /):
        return super().__new__(cls, (cls.format(item) for item in items))

    def __contains__(self, target: _t.Any) -> bool:
        return super().__contains__(self.format(target))

    def get(self, item: str, default=None) -> str | None:
        return dunder if (dunder := self.format(item)) in self else default
