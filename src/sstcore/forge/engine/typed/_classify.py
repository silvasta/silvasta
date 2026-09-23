"""
Extract Type Information from Protocols and Classes for Stub Generation

- Execute functional stack together with Class Builder and Meta Constructors


                      DependencyLevel.sstcore.forge.engine.typed[0]
"""

__all__: list[str] = [
    "MemberKind",
    "classify_member",
]

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from . import _types as _t


@dataclass(frozen=True, slots=True)
class ProtoMember:
    """One renderable slot on a class/protocol."""

    name: str
    kind: MemberKind
    annotation: str = "Any"
    signatures: tuple[str, ...] = ()


class MemberKind(Enum):
    ATTR = auto()
    PROP = auto()
    METHOD = auto()


def classify_member(
    name: str, raw: Any, hints: dict[str, Any]
) -> _t.AttrKind | None:
    match raw:
        case property():
            return "property"
        case Callable():
            return "method"
        case _:
            if name in hints:
                return "attribute"
    return None
