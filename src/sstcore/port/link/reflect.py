"""
reflect

.
"""

import typing as _t
from functools import cached_property as _cached_property
from inspect import cleandoc as _cleandoc

from ._base import ReflectorBase
from .data import Doc, _Side, spec


class Reflecting(_t.Protocol):
    def __call__(self, target: _t.Any, name: str, /) -> _t.Any:
        """Set the new Value for the attribute into the target"""


class Reflect(ReflectorBase):
    __call__: Reflecting

    def core(self, target: type, name: str, /):
        _target = self.resolve(target, name)
        self.strategy(target, name)

    @property
    def strategy(self):
        match self.mode:
            case "soft":
                return self.polite
            case "hard":
                return self.direct

    def direct(self, target: type, name: str, /):
        return target.__dict__.get(name)

    def polite(self, target: type, name: str, /, default=None):
        return getattr(target, name, default)

    def resolve(self, cls: type, attr_name: str, /):
        match attr := self(cls, attr_name):
            case classmethod() | staticmethod():
                return attr.__func__
            case property() | _cached_property():
                return attr
            case _ if callable(attr):
                return attr
            case _:
                return None

    def base(self, base: type, name: str, /) -> object | None:
        return base if not name else self(base, name)

    def doc(self, target: _t.Any, name: str, /) -> str:
        raw: _t.Any | None = (
            self.polite(target, "__doc__")
            if name
            else self.direct(target, "__doc__")
        )
        return self.clean(raw)

    def clean(self, doc: str | _t.Any, /):
        return _cleandoc(doc) if isinstance(doc, str) and doc else ""

    def links(self, target, /):
        self.core(target, "__links__")


_reflect = Reflect()


def _idea_get_original_doc(target, name="__portlink_orig_doc__") -> str:
    if doc := _reflect.direct(target, name):
        return doc

    return _reflect.doc(target, name)


def _idea_get_original_doc(target, name="__portlink_orig_doc__") -> str:
    return (
        doc
        if (doc := _reflect.direct(target, name))
        else _reflect.doc(target, name)
    )


def _own_text(base: type, name: str, side: _Side, payload: object, /) -> str:
    """Original fragment for this defining class. Never a previously merged blob."""
    links = _reflect(payload, "__links__")
    # TASK: compare with current dto
    # - find then better way to compare...
    if isinstance(links, frozenset):
        for item in links:
            if (
                isinstance(item, Doc)
                and item.owner is base
                and item.name == name
                and item.side == side
            ):
                return item.text
        return ""
    return _reflect.doc(payload, name)


def _find_injection_target(cls: type, attr_name: str) -> _t.Any | None:
    if target := _reflect.direct(cls, attr_name):
        _stash_raw_doc(target)
        return target
    for base in cls.__mro__:
        if spec.ignores(base):
            continue
        if target := _reflect.direct(base, attr_name):
            _stash_raw_doc(target)
            return target
    return None


def _extract_origins(
    cls: type, attr: str, side: _t.Literal["port", "plug"]
) -> _t.Iterator[Doc]:
    # NEXT:
    # NEXT:
    for base in cls.__mro__:
        if spec.ignores(base):
            continue

        if portlinks := _reflect.direct(base, "__portlinks__"):
            if attr in portlinks:
                yield from portlinks[attr]
                continue

        if attr not in base.__dict__:
            continue

        _target = base if attr == "__doc__" else _reflect.direct(base, attr)
        if text := _reflect.doc(_target, attr):
            yield Doc(text, attr, base)
