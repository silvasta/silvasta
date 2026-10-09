"""
Solve a Simple Problem with elegantly building new Types

                               DependencyLevel.sstcore.port.link[0]
"""

# IDEA: merge with Data

__all__: list[str] = [
    "DunderStore",
    "DunderFormatMixin",
    "DunderDict",
    "DunderSet",
]


from collections.abc import Iterable
from typing import Any, Protocol

from ..calling import Stringable


class DunderStore(Protocol):
    def __init__(self, dunders: Iterable[str] = ()): ...
    def get(self, name: str, *args, **kwargs) -> str | None: ...


class DunderFormatMixin:
    @staticmethod
    def format(item: Stringable, /) -> str:
        return f"__{DunderFormatMixin.extract(item)}__"

    @staticmethod
    def extract(item: Stringable, /) -> str:
        return str(item).strip("_")


class DunderDict(DunderFormatMixin, dict):
    def __init__(self, dunders: Iterable[str] = ()):
        for method in dunders:
            self[method] = None

    def __setitem__(self, key, _value=None):
        super().__setitem__(key.strip("_"), f"__{key.strip('_')}__")


class DunderSet(DunderFormatMixin, frozenset):
    def __new__(cls, items: Iterable[str] = (), /):
        return super().__new__(cls, (cls.format(item) for item in items))

    def __contains__(self, target: Any) -> bool:
        return super().__contains__(self.format(target))

    def get(self, item: str, default=None) -> str | None:
        return dunder if (dunder := self.format(item)) in self else default
