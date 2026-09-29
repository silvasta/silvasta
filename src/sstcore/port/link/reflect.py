"""
reflect

.
"""

import typing as _t
from functools import cached_property as _cached_property
from inspect import cleandoc as _cleandoc

from .define import Reflecting
from .operator import ReflectorBase


class Reflect(ReflectorBase, id="reflector"):
    __call__: Reflecting
    mode: _t.Literal["soft", "hard"] = "soft"  # IDEA: combine with inject?

    def __core__(self, target: type, attr: str, /):
        _target = self.resolve(target, attr)
        self.strategy(target, attr)

    @property
    def strategy(self) -> Reflecting:  # IDEA: combine with inject? in EasyCore
        match self.mode:
            case "soft":
                return self.polite
            case "hard":
                return self.direct

    def direct(self, target: type, attr: str, /):
        return target.__dict__.get(attr)

    def polite(self, target: type, attr: str, /, default=None):
        return getattr(target, attr, default)

    def resolve(self, cls: type, attr: str, /):
        match attr := self(cls, attr):
            case classmethod() | staticmethod():
                return attr.__func__
            case property() | _cached_property():
                return attr
            case _ if callable(attr):
                return attr
            case _:
                return None

    def base(self, base: type, name: str, /) -> object | None:
        # CHECK: how?, where?
        return base if not name else self(base, name)

    def doc(self, target: _t.Any, name: str, /) -> str:
        # REMOVE: when EasyAccess works, or better not?
        # IMPORTANT: check dispatch: easy/soft?
        raw: _t.Any | None = (
            self.polite(target, "__doc__")
            if name
            else self.direct(target, "__doc__")
        )
        return self.clean(raw)

    def clean(self, doc: str | _t.Any, /):
        return _cleandoc(doc) if isinstance(doc, str) and doc else ""

    def links(self, target, /):
        # REMOVE: when EasyAccess works
        self.core(target, "__links__")


_reflect = Reflect()
