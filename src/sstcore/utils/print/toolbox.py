"""Collect Specialized Tools - for special occasions"""

from pathlib import Path

from rich.table import Table
from rich.tree import Tree

from ...contract.external import RichProtocol
from ..color import colorize
from ..tree import SimpleTreeNode

# LATER: colapse with ToolMixin?


def path_exists_table(paths: list[Path], title=None, header="Path") -> Table:
    """Check if Paths exist and visualize in Table"""

    table = Table(title=title)
    table.add_column("Status", justify="center")
    table.add_column(header, style="cyan")

    for path in paths:
        status: str = "✅" if path.exists() else ""
        table.add_row(status, colorize.path(path))

    return table


def dict_table(
    target: dict,
    style="cyan",
    show_type: bool | tuple[bool, bool] = (False, True),
) -> Table:
    """Visualize Dict as Rich Table"""

    table = Table(style=style)

    show_key_type, show_value_type = (
        show_type if isinstance(show_type, tuple) else (show_type, show_type)
    )

    table.add_column("Key", justify="left", style="green")
    if show_key_type:
        table.add_column("Type Key", justify="center", style="magenta")

    table.add_column("Value", style="blue", justify="left")
    if show_value_type:
        table.add_column("Type Value", style="magenta")

    for key, value in target.items():
        row: list[RichProtocol] = [
            key,
            *([type(key).__name__] if show_key_type else []),
            value,
            *([type(value).__name__] if show_value_type else []),
        ]
        table.add_row(*row)

    return table


def tree_graph(
    simple_tree: SimpleTreeNode,
    max_depth: int | None = None,
    root: str = "bold magenta",
    node: str = "by_level",
    guide: str = "bold white",
    hide_root=False,
) -> Tree:
    """Visualize SimpleTreeNode as nested Rich Tree"""

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
            child_label: str = _apply_style(branch.display_label, color=color)
            child_branch: Tree = current_branch.add(child_label)

            build_branch(branch, child_branch, current_depth + 1)

    build_branch(simple_tree, visual_tree, current_depth=1)

    return visual_tree
