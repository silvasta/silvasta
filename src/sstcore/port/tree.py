from collections.abc import Sequence
from typing import Any, Protocol


class SimpleTree(Protocol):
    """Protocol for any hierarchical tree node."""

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
