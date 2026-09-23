"""
Extract Type Information from Protocols and Classes for Stub Generation

- Execute functional stack together with Class Builder and Meta Constructors


                      DependencyLevel.sstcore.forge.engine.typed[0]
"""

__all__: list[str] = [
    "is_protocol",
    "is_private_not_calling",
    "is_typing_meta_blueprint",
]

from typing import Generic, Protocol

from . import _types as _t

x: _t.ProtoType


def is_protocol(cls: type) -> bool:
    """Check type first to avoid TypeError on second call"""
    return (
        isinstance(cls, type)
        and issubclass(cls, Protocol)
        and getattr(cls, "_is_protocol", False)
    )


def is_private_not_calling(attr: str) -> bool:
    exclude: set[str] = {"__call__", "__getitem__"}
    return attr.startswith("_") and attr not in exclude


def is_typing_meta_blueprint(cls: type) -> bool:
    return cls in (object, Protocol, Generic)
