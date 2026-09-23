"""
Collect Types for Hinting

- Even if it is just for the more expressive Name

                      DependencyLevel.sstcore.forge.engine.typed[0]
"""

__all__: list[str] = [
    "ProtoType",
    "AttrName",
    "RawObject",
    "PublicMember",
    #
    "AttrKind",
    "TypeHints",
    "OverLoads",
]

from collections.abc import Callable, Sequence
from typing import Any, Literal

type ProtoType = type
type AttrName = str
type RawObject = object
type PublicMember = tuple[AttrName, RawObject, AttrKind]

type AttrKind = Literal["property", "method", "attribute"]
type TypeHints = dict[str, Any]
type OverLoads = Sequence[Callable[..., Any]]
