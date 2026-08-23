from collections.abc import Sequence
from enum import StrEnum, auto
from typing import Any, Protocol


class SimpleTree(Protocol):
    """Protocol for any hierarchical tree node."""

    # NEXT: modify
    # NEXT: modify
    # NEXT: modify
    # NEXT: modify
    # NEXT: modify
    # NEXT: modify
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


class ASTree(SimpleTree, Protocol):
    """Protocol for path-based tree nodes."""

    # NEXT: modify
    # NEXT: modify


class _CSTree(SimpleTree, Protocol):
    # NEXT: modify
    """Protocol for path-based tree nodes."""

    # NEXT: modify
    # NEXT: modify

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
