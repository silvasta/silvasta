"""Assemble ToolBox to Printer"""

__all__: list[str] = [
    "ToolMixin",
]
from pathlib import Path

from rich.table import Table
from rich.tree import Tree

from ...tree import SimpleTreeNode
from .. import toolbox
from ..blueprint import Printer

# LATER: Tree DTO?
# LATER: collapse with toolbox?


class ToolMixin:
    """Provide specialized Visualizations from the ToolBox"""

    def path_exists_table(
        self: Printer, paths: list[Path], title=None, header="Path"
    ) -> None:
        """Check if Paths Exist or Missing and render result"""
        table: Table = toolbox.path_exists_table(paths, title, header)
        self(table)

    def dict_table(  # LATER: create colorize.table?
        self: Printer,
        target: dict,
        header="Dict Inspection",
        show_type: bool | tuple[bool, bool] = (True, True),
        style="green",
    ):
        """Render colorful Debug Dict, optional with Key or Value Type"""
        if header:
            self.header(header, title="Dict Inspection", style=style)
        table: Table = toolbox.dict_table(target, style, show_type)
        self(table)

    def tree_graph(
        self: Printer,
        simple_tree: SimpleTreeNode,
        max_depth: int | None = None,
        root: str = "bold magenta",
        node: str = "by_level",
        guide: str = "bold white",
        hide_root=False,
    ) -> None:
        """Render SimpleTreeNode in Terminal"""
        visual_tree: Tree = toolbox.tree_graph(
            simple_tree, max_depth, root, node, guide, hide_root
        )
        self(visual_tree)
