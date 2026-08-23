"""
Generate Simple Tree with Nodes that have Branches

- SimpleTreeNode: Provide basic layout
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "SimpleTreeNode",
]

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Self


# NEXT: view
# NEXT: view
# NEXT: view
# NEXT: view
@dataclass(frozen=True)
class SimpleTreeNode:
    """Build Node with 0..N subnodes each with own subnodes"""

    name: str
    id: str | None = None
    branches: Sequence[Self] = field(default_factory=list)

    @property
    def display_label(self) -> str:
        """Show public representation e.g. in Selector or Visualization"""
        return self.name

    @property
    def identifier(self):
        """Provide value that allows identification (No test for uniqness here!)"""
        return self.id


# NEXT: generate SimpleTree
# NEXT: generate SimpleTree
# NEXT: generate SimpleTree
