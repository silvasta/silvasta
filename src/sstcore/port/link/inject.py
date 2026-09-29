"""
inject

.
"""

import typing as _t

from .define import Injecting
from .operator import InjectorBase


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


def _inject_safe_example(target: _t.Any, value: str, /, attr: str):
    with Inject(core=_inject_doc_raw) as injector:
        injector(target, attr, value)


def _inject_doc_raw(target: _t.Any, value: str):
    object.__setattr__(target, "__doc__", value)
