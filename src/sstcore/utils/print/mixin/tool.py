from pathlib import Path

from rich.table import Table
from rich.tree import Tree

from ...tree import SimpleTreeNode
from .. import toolbox
from ..base import BasePrinter
from ..stylebox import style


class ToolMixin(BasePrinter):
    ### -- --- -- --- -- --- -- --- -- --- -- --- -- --- -- --- -- --- -- ---
    ### Tool Kit
    ### -- --- -- --- -- --- -- --- -- --- -- --- -- --- -- --- -- --- -- ---

    def path_exists_table(self, paths: list[Path], title=None, header="Path"):
        """Check if Paths exist and visualize in Table"""

        table: Table = toolbox.path_exists_table(
            paths, self._format, title, header
        )

        self(table)

    # TASK: figure out method to dynamically apply args, decorator?
    # For example, provide with 1 set:
    # - header, header_style etc
    # - different other color or style attributes

    def dict_table(
        self,
        target: dict,
        header="Dict Inspection",
        show_type: bool | tuple[bool, bool] = (True, True),
        _style="green",  # REMOVE: after removing: type style
    ):
        """Debug Dict"""
        if header:
            # TASK: args, title_header?
            # - use intermediates like self.title or self.header
            header: str = self._colorize(header, style="bold white")
            title: str = self._colorize("Dict Inspection", style="white")
            self.panel(
                header,
                title=title,
                title_align="right",
                style=_style,
            )

        table: Table = toolbox.dict_table(
            target, self._format, style=_style, show_type=show_type
        )

        self(table)

    def tree_graph(
        self,
        simple_tree: SimpleTreeNode,
        max_depth: int | None = None,
        root: style = "bold magenta",
        node: style = "by_level",
        guide: style = "bold white",
        hide_root=False,
    ) -> None:
        """Visualizes a SimpleTreeNode model as a nested Rich Tree"""

        visual_tree: Tree = toolbox.tree_graph(
            simple_tree, max_depth, root, node, guide, hide_root
        )

        self(visual_tree)
