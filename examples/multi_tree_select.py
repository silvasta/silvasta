from pathlib import Path

import fire

from sstcore.exceptions import TuiSelectorError
from sstcore.tui.tree_selector import TreeSelectorApp
from sstcore.utils import FolderScanner, PathTreeNode, SimpleTreeNode, printer
from sstcore.utils.path import get_project_root
from sstcore.utils.tree import examples

SCAN_ROOT: Path = get_project_root()


def main():
    printer.title("Start of name_parsing")
    fire.Fire(SelectTreeTasks)


class SelectTreeTasks:
    def simple(self):
        tree: SimpleTreeNode = examples.simple_tree()
        launch_selector(tree)

    def big(self):
        tree: SimpleTreeNode = examples.big_tree()
        launch_selector(tree)

    def scan(self):
        tree: PathTreeNode = FolderScanner(SCAN_ROOT).tree()
        launch_selector(tree)


def launch_selector(tree: SimpleTreeNode):
    """Select 1 or multiple nodes in the Tree"""

    tui = TreeSelectorApp(
        sst_tree=tree,
    )
    selected_nodes: list | None = tui.run()

    if not selected_nodes:
        raise TuiSelectorError

    printer.lines_with_len(
        name="Successfully selected nodes",
        lines=selected_nodes,
        style="success",
    )


if __name__ == "__main__":
    main()
