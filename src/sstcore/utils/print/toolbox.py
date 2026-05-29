from collections.abc import Callable
from pathlib import Path
from typing import Any

from rich.table import Table
from rich.tree import Tree

from ..simple_tree import SimpleTreeNode
from .stylebox import style


def path_exists_table(
    paths: list[Path], _format: Callable[[Any], str], title=None, header="Path"
) -> Table:
    """Check if Paths exist and visualize in Table"""

    table = Table(title=title)
    table.add_column("Status", justify="center")
    table.add_column(header, style="cyan")

    for path in paths:
        status: str = "✅" if path.exists() else ""
        table.add_row(status, _format(path))

    return table


def _unpack_bool_tuple(  # LATER: check where else this can be used
    show_type: bool | tuple[bool, bool],
) -> tuple[bool, bool]:

    if isinstance(show_type, bool):
        if show_type:
            return True, True
        else:
            return False, False
    else:
        return show_type


def dict_table(
    target: dict,
    _format: Callable[[Any], str],
    show_type: bool | tuple[bool, bool] = (True, True),
) -> Table:
    """Debug Dict"""

    key_type, value_type = _unpack_bool_tuple(show_type)

    table = Table(style="cyan")

    table.add_column("Key", justify="left", style="green")

    if key_type:
        table.add_column("Type Key", justify="center", style="magenta")

    table.add_column("Value", style="blue", justify="left")

    if value_type:
        table.add_column("Type Value", style="magenta")

    for key, value in target.items():
        to_print: list[str] = []
        to_print.append(_format(key))
        if key_type:
            to_print.append(_format(type(key)))
        to_print.append(_format(value))
        if value_type:
            to_print.append(_format(type(value)))
        table.add_row(*to_print)

    return table


def tree_graph(
    simple_tree: SimpleTreeNode,
    max_depth: int | None = None,
    root: style = "bold magenta",
    node: style = "by_level",
    guide: style = "bold white",
    hide_root=False,
) -> Tree:
    """Visualizes a SimpleTreeNode model as a nested Rich Tree"""

    _node_styles: dict[int, str] = {
        1: "green",
        2: "yellow",
        3: "white",
    }

    def _apply_style(node_label: str, color: style | int = ""):
        if isinstance(color, int):
            color: str = _node_styles.get(color, "red")
        return f"[{color}]{node_label}[/]" if color else node_label

    visual_tree = Tree(
        label=_apply_style(simple_tree.name, color=root),
        guide_style=guide,
        hide_root=hide_root,
        # style="on white",  # Applies a background color to the whole tree area
    )

    def build_branch(
        tree_node: SimpleTreeNode,
        current_branch: Tree,
        current_depth: int,
    ):
        if max_depth is not None and current_depth >= max_depth:
            return

        nonlocal node
        color: style | int = current_depth if node == "by_level" else node

        for branch in tree_node.branches:
            child_label: str = _apply_style(branch.display_label, color=color)
            child_branch: Tree = current_branch.add(child_label)

            build_branch(branch, child_branch, current_depth + 1)

    build_branch(simple_tree, visual_tree, current_depth=1)

    return visual_tree
