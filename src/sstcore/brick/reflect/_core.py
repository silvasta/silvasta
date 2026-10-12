"""
Inspect arbitrary objects and safely pull out specific attributes

- Extract Type Information from Protocols and Classes for Stub Generation
- Execute functional stack together with Class Builder and Meta Constructors

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "clsname",
    "funcname",
    "is_private",
    "is_dunder",
    "is_protocol",
    "is_private_not_calling",
    "is_typing_generic",
]


from collections.abc import Sequence
from typing import Any, Generic, Protocol

from ._attr import _attr


def clsname(target: Any, /, default="") -> str:
    """Extract name from instance or class"""
    default: str = default or type(target).__name__
    return _attr(target, attrs=("__name__",), default=default)


def funcname(target: Any, /, default="Func") -> str:
    """Check attribute list, provide match or default"""
    attrs: Sequence[str] = ("__name__", "__qualname__")
    return _attr(target, attrs, default)


def is_private(_attr: str) -> bool:  # LATER: str|list[str]->bool|list[bool]
    return _attr.startswith("_")


def is_dunder(_attr: str) -> bool:  # LATER: str|list[str]->bool|list[bool]
    return _attr.startswith("__") and _attr.endswith("__")


def is_protocol(cls: type) -> bool:
    """Check type first to avoid TypeError on second call"""
    return (
        isinstance(cls, type)
        and issubclass(cls, Protocol)
        and getattr(cls, "_is_protocol", False)
    )


def is_private_not_calling(attr: str) -> bool:
    # TODO: resolve by AttrFilter?
    exclude: set[str] = {"__call__", "__getitem__"}
    return attr.startswith("_") and attr not in exclude


def is_typing_generic(cls: type) -> bool:
    return cls in (object, Protocol, Generic)
