"""
inject

.
"""

import typing as _t
from inspect import cleandoc as _cleandoc

from .data import Doc
from .define import Injecting
from .operator import InjectorBase

# TODO:


def _inject_doc_raw(target: _t.Any, value: str):
    object.__setattr__(target, "__doc__", value)


def _inject_safe_example(target: _t.Any, value: str, /, attr: str):
    with Inject(core=_inject_doc_raw) as injector:
        injector(target, attr, value)


class Inject(InjectorBase, id="injector"):
    __call__: Injecting
    mode: _t.Literal["soft", "hard"] = "soft"

    def __core__(self, target: _t.Any, value: _t.Any, attr: str):
        _target = self.resolve(target, attr)
        self.strategy(_target, value, attr)

    @property
    def strategy(self) -> Injecting:
        match self.mode:
            case "soft":
                return self.polite
            case "hard":
                return self.direct

    def direct(self, target: _t.Any, value: _t.Any, attr: str):
        with self:  # MOVE: to EasyCatchL2??
            object.__setattr__(target, attr, value)

    def polite(self, target: _t.Any, value: _t.Any, attr: str):
        with self:  # MOVE: to EasyCatchL2??
            setattr(target, attr, value)

    def resolve(self, target: _t.Any, attr: str) -> _t.Any:
        if attr == "__doc__":  # CHECK: where is this needed?
            if isinstance(target, property) and target.fget is not None:
                return target.fget
            if hasattr(target, "__func__"):
                return target.__func__
        return target

    def doc(self, target: _t.Any, value: str, /):
        self.core(target, value, attr="__doc__")

    def links(self, target: _t.Any, value: _t.Any, /):
        self.core(target, value, attr="__links__")


_injector = Inject()
_injector(_injector, "", "")


ORIG_DOC = "__portlink_orig_doc__"


def _record_links(self, cls: type, protocol: type) -> None:
    """Lightweight history on the class."""
    links = getattr(cls, "__port_links__", set())
    links.add(protocol)
    # Use object.__setattr__ in case someone makes the class frozen later
    try:
        cls.__port_links__ = links
    except AttributeError, TypeError:
        pass


def _idea_set_new_original_doc(target: _t.Any, new_doc: str):
    _original_doc = getattr(target, "__doc__", None)
    if not _original_doc or hasattr(target, ORIG_DOC):
        return
    with Inject() as injector1:
        injector1.hard(target, ORIG_DOC, _cleandoc(_original_doc))
        with Inject() as injector2:
            injector2.doc(target, new_doc)


def _idea_set_new_original_doc(target: _t.Any, new_doc: str):  # CHECK:
    if not hasattr(target, "__portlink_orig_doc__"):
        if not (original_doc := getattr(target, "__doc__", None)):
            return
        with Inject(mode="soft") as injector:
            target.__portlink_orig_doc__ = _cleandoc(original_doc)
            injector.doc(target, new_doc)  # NOTE: maybe in new context?

    @staticmethod
    def _attach_history(target: object, fragments: list[Doc]) -> None:
        """Attach contributor info directly on the function/object."""
        if not hasattr(target, "__portlink_sources__"):
            try:
                target.__portlink_sources__ = set()
            except AttributeError, TypeError:
                return

        for f in fragments:
            target.__portlink_sources__.add(f.key)


def _inject_links(target: object, doc: str, data: _t.Sequence[Doc], /) -> None:
    """Stamp ``__doc__`` and ``__links__``. Worst case: nothing changes."""
    if not doc:
        return

    if getattr(target, "__links__", None) == (links := frozenset(data)):
        return  # MOVE: reflect

    with Inject(mode="soft") as injector1:
        injector1.doc(target, doc)
        # TASK: check early return on fail!

    with Inject(mode="hard") as injector2:
        injector2.link(target, links)
        # AI: what about the order of with and injectors?
        with Inject(mode="soft") as injector3:
            injector3.link(target, links)

    with Inject(mode="soft") as injector2:
        # AI: what about the order of with and injectors?
        with Inject(mode="hard") as injector3:
            injector3.link(target, links)
        injector2.link(target, links)
