"""
Tree Printer

- temporary module
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, Self

from rich.console import Console
from rich.tree import Tree

console = Console()


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


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class TreePrinter:
    def __call__(self, *args, **kwargs):
        console.print(*args, **kwargs)

    def tree_graph(  # IDEA: MRO display???
        self,
        simple_tree: SimpleTreeNode,
        max_depth: int | None = None,
        root: str = "bold magenta",
        node: str = "by_level",
        guide: str = "bold white",
        hide_root=False,
    ) -> None:
        """Render SimpleTreeNode as nested Rich Tree in Terminal"""

        _node_styles: dict[int, str] = {
            1: "green",
            2: "yellow",
            3: "white",
        }

        def _apply_style(node_label: str, color: str | int = ""):
            if isinstance(color, int):
                color: str = _node_styles.get(color, "red")
            return f"[{color}]{node_label}[/]" if color else node_label

        visual_tree = Tree(
            label=_apply_style(simple_tree.name, color=root),
            guide_style=guide,
            hide_root=hide_root,
        )

        def build_branch(
            tree_node: SimpleTreeNode,
            current_branch: Tree,
            current_depth: int,
        ):
            if max_depth is not None and current_depth >= max_depth:
                return

            nonlocal node
            color: str | int = current_depth if node == "by_level" else node

            for branch in tree_node.branches:
                child_label: str = _apply_style(
                    branch.display_label, color=color
                )
                child_branch: Tree = current_branch.add(child_label)

                build_branch(branch, child_branch, current_depth + 1)

        build_branch(simple_tree, visual_tree, current_depth=1)

        self(visual_tree)
