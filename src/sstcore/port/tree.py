"""
Define the Shape of Nodes and Edges

- preferably without too much cycles
                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "SimpleTree",
    "PathTree",
    "AsTree",
    "AstKind",
    "CsTree",
]


from collections.abc import Sequence
from enum import StrEnum, auto
from typing import Any, Protocol


class SimpleTree(Protocol):
    """Protocol for any hierarchical tree node."""

    # IMPORTANT: modify
    @property
    def name(self) -> str: ...
    @property
    def id(self) -> str | None: ...
    @property
    def display_label(self) -> str: ...
    @property
    def identifier(self) -> Any: ...
    @property
    def branches(self) -> Sequence[SimpleTree]: ...


class PathTree(SimpleTree, Protocol):
    """Protocol for path-based tree nodes."""

    @property
    def path(self) -> Any: ...


class AsTree(SimpleTree, Protocol):
    # NEXT: modify
    """Protocol for path-based tree nodes."""


class CsTree(SimpleTree, Protocol):
    # NEXT: modify
    """Protocol for path-based tree nodes."""

    @property
    def path(self) -> Any: ...


"""G45"""


class AstKind(StrEnum):
    MODULE = auto()
    CLASS = auto()
    DEF = auto()
    ASYNC_DEF = auto()
    ASSIGN = auto()  # optional module-level


class ScanModeG45(StrEnum):
    RAW = auto()
    API = auto()


class ApiStyle(StrEnum):
    COMPACT = auto()
    STUB = auto()
