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


from collections.abc import Sequence
from typing import Any

from ._attr import _attr as attr_core


def clsname(target: Any, /, default="") -> str:
    """Extract name from instance or class"""
    default: str = default or type(target).__name__
    return attr_core(target, attrs=("__name__",), default=default)


def funcname(target: Any, /, default="Func") -> str:
    """Check attribute list, provide match or default"""
    attrs: Sequence[str] = ("__name__", "__qualname__")
    return attr_core(target, attrs, default)


def objname(target: Any, /, default: str = "") -> str:
    """Resolves the best identifying name for ANY object"""
    if name := attr_core(target, ("__qualname__", "__name__")):
        return name
    return default or attr_core(
        type(target), "__qualname__", type(target).__name__
    )
