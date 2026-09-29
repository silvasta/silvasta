"""
reflect

.
"""

import typing as _t
from functools import cached_property as _cached_property
from inspect import cleandoc as _cleandoc

from .data import Doc, spec
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
        # REMOVE: when EasyAccess works
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


def _find_injection_target(cls: type, attr: str) -> _t.Any | None:
    if target := _reflect.direct(cls, attr):
        _stash_raw_doc(target)
        return target
    for base in cls.__mro__:
        if spec.ignores(base):
            continue
        if target := _reflect.direct(base, attr):
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
