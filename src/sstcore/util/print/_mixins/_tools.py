"""Assemble Specialized Visualizations directly on the"""

__all__: list[str] = [
    "ToolMixin",  # Consider renaming to InspectMixin in the future!
]

from pathlib import Path

from rich.console import RichCast
from rich.table import Table
from rich.tree import Tree

from ....brick.color import colorize
from ...tree import SimpleTreeNode
from ._layout import _NoLayoutBase


class ToolMixin(_NoLayoutBase):
    """Provide specialized Visualizations for debugging and introspection"""

    def path_exists_table(
        self, paths: list[Path], title=None, header="Path"
    ) -> None:
        """Check if Paths Exist or Missing and render result"""
        table = Table(title=title)
        table.add_column("Status", justify="center")
        table.add_column(header, style="cyan")

        for path in paths:
            status: str = "✅" if path.exists() else ""
            table.add_row(status, colorize.path(path))

        self(table)

    def dict_table(
        self,
        target: dict,
        header="Dict Inspection",
        show_type: bool | tuple[bool, bool] = (True, True),
        style="green",
    ) -> None:
        """Render colorful Debug Dict, optional with Key or Value Type"""
        if header:
            self.header(header, title="Dict Inspection", style=style)

        table = Table(style=style)

        show_key_type, show_value_type = (
            show_type
            if isinstance(show_type, tuple)
            else (show_type, show_type)
        )

        table.add_column("Key", justify="left", style="green")
        if show_key_type:
            table.add_column("Type Key", justify="center", style="magenta")

        table.add_column("Value", style="blue", justify="left")
        if show_value_type:
            table.add_column("Type Value", style="magenta")

        for key, value in target.items():
            row: list[RichCast] = [
                key,
                *([type(key).__name__] if show_key_type else []),
                value,
                *([type(value).__name__] if show_value_type else []),
            ]
            table.add_row(*row)

        self(table)

    def tree_graph(
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
