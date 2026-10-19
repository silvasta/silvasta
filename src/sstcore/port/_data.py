"""
Solve a Simple Problem with elegantly building new Types

                               DependencyLevel.sstcore.port.link[0]
"""

__all__: list[str] = [
    "PortEmit",
    "Channels",
    "DunderStore",
    "DunderFormatMixin",
    "DunderDict",
    "DunderSet",
]


import os
from collections.abc import Iterable
from typing import Any, Protocol

from ._types import _Stringable


class PortEmit[**P](Protocol):  # MOVE:
    def __call__(self, *args, sender: Any = None, **kwargs) -> None:
        """Define the message structure of port internal events"""


#  LINE: -- Debug Channel (Tap) -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Channels(frozenset):
    """Guard the active Channels and Rules for Matching"""

    def __new__(cls, env_var="SST_DEBUG", default=()):
        env = (*os.getenv(env_var, "").split(","), *default)
        return super().__new__(cls, (c for e in env if (c := cls.format(e))))

    @classmethod
    def format(cls, target: str, /) -> str:
        return target.strip().lower()

    def has(self, flag: str, /) -> bool:
        """Check formatted flag directly (bypass wildcard/substring match)"""
        return super().__contains__(self.format(flag))

    def __contains__(self, target: Any) -> bool:
        """Check if the target matches an active channel"""

        if not self or not isinstance(target, str):
            return False

        low: str = self.format(target)
        if "port.link" in low and not self.has("link"):
            return False

        if self.has("*"):
            return True

        return any(scope in low for scope in super().__iter__())


#  LINE: -- Dunders (PortLink __getattr__) -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class DunderStore(Protocol):
    def __init__(self, dunders: Iterable[str] = ()): ...
    def get(self, name: str, *args, **kwargs) -> str | None: ...


class DunderFormatMixin:
    @staticmethod
    def format(item: _Stringable, /) -> str:
        return f"__{DunderFormatMixin.extract(item)}__"

    @staticmethod
    def extract(item: _Stringable, /) -> str:
        return str(item).strip("_")


class DunderDict(DunderFormatMixin, dict):
    """Outdated initial attempt..."""

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
