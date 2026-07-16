from pathlib import Path

from rich.table import Table
from rich.tree import Tree

from ...tree import SimpleTreeNode
from .. import toolbox
from ..blueprint import Printer

# LATER: Table or even Tree DTO?


class ToolMixin:
    """Connect with the Special-Print ToolBox"""

    def path_exists_table(
        self: Printer, paths: list[Path], title=None, header="Path"
    ) -> None:
        """Check Paths and show table with existing or missing locations"""
        table: Table = toolbox.path_exists_table(paths, title, header)
        self(table)

    def dict_table(
        self: Printer,
        target: dict,
        header="Dict Inspection",
        show_type: bool | tuple[bool, bool] = (True, True),
        style="green",
    ):
        """Create colorful Debug Dict if desired with types of key and value"""
        if header:
            header: str = self.color(header, color="bold white")
            title: str = self.color("Dict Inspection", color="white")
            self.panel(header, title=title, title_align="right", style=style)
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
        """Render SimpleTreeNode model as nested Rich Tree"""
        visual_tree: Tree = toolbox.tree_graph(
            simple_tree, max_depth, root, node, guide, hide_root
        )
        self(visual_tree)
