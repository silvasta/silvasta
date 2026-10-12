"""
Inspect arbitrary objects and safely pull out specific attributes

- Extract Type Information from Protocols and Classes for Stub Generation
- Execute functional stack together with Class Builder and Meta Constructors

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "clsname",
    "funcname",
    "objname",
]


import sys
from collections.abc import Sequence
from types import ModuleType
from typing import Any

from . import _attr


def clsname(target: Any, /, default="") -> str:
    """Extract name from instance or class"""
    default: str = default or type(target).__name__
    return _attr(target, ("__name__",), default)  # ty:ignore


def funcname(target: Any, /, default="Func") -> str:
    """Check attribute list, provide match or default"""
    attrs: Sequence[str] = ("__name__", "__qualname__")
    return _attr(target, attrs, default)  # ty:ignore


def objname(target: Any, /, default: str = "") -> str:
    """Resolves the best identifying name for ANY object"""
    if name := _attr(target, attrs := ("__qualname__", "__name__")):  # ty:ignore
        return name
    if type_name := _attr(type(target), attrs):  # ty:ignore
        return type_name
    return default or type(target).__name__


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CallableModule(ModuleType):
    def __call__(self, target: Any, /, default: str = ""):
        return objname(target, default)


sys.modules[__name__].__class__ = CallableModule
