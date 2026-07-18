from enum import StrEnum

from loguru import logger
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Footer, Header, Tree
from textual.widgets.tree import TreeNode

from ..utils.print import printer
from ..utils.tree import SimpleTreeNode

# TASK: check folder(edges != leaf) and how they are counted


class MultiSelectTree(Tree[str]):
    """
    Render SimpleTreeNode with Selectable Nodes and provide Result

    - Implement VIM Navigation and disable default selection keys

    """

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=True),
        Binding("k", "cursor_up", "Up", show=True),
        Binding("h", "collapse_parent", "Collapse/Up", show=True),
        Binding("l", "expand_child", "Expand/Down", show=True),
        Binding("space", "toggle_select", "Select Node"),
        Binding("enter", "submit", "Submit Selection"),
    ]

    class NodeToggled(Message):
        """Emitted when a node is toggled via spacebar"""

        def __init__(self, node: TreeNode) -> None:
            self.node: TreeNode = node
            super().__init__()

    class Submitted(Message):
        """Emitted when the user finalizes their selection"""

    def action_collapse_parent(self) -> None:
        """Key H: Collapse node or move to parent if already collapsed"""
        if node := self.cursor_node:
            if node.is_expanded and node.allow_expand:
                node.collapse()

    def action_expand_child(self) -> None:
        """Key L: Expand node or move to first child if already expanded"""
        if node := self.cursor_node:
            if not node.is_expanded and node.allow_expand:
                node.expand()

    def action_toggle_select(self) -> None:
        """Key Space: Toggle node Selection State"""
        if self.cursor_node:
            self.post_message(self.NodeToggled(self.cursor_node))

    def action_submit(self) -> None:
        """Key Enter: Finish Selection and provide Result"""
        self.post_message(self.Submitted())


class TreeSelectorApp(App[list]):
    """Displays Tree in transient app and return the Selected Node"""

    BINDINGS = [
        Binding("escape", "quit_without_selection", "Cancel"),
        Binding("q", "quit_without_selection", "Quit"),
    ]

    class Sort(StrEnum):
        """Govern Action Selection and Execution"""

        SELECTION = "s"  # follow order of selection
        ALPHABETIC = "a"

    sort_method: Sort = Sort.SELECTION

    def __init__(
        self,
        sst_tree: SimpleTreeNode,
        sort_method: str = "",
        pre_select: list | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.sst_tree: SimpleTreeNode = sst_tree
        if sort_method:
            self._setup_sort_method(sort_method)
        self.selected_identifiers: dict[str, None] = {
            uid: None for uid in (pre_select or [])
        }
        self.original_labels: dict[str, str] = {}

    def _setup_sort_method(self, sort_method: str):
        try:
            self.sort_method: self.Sort = self.Sort(sort_method)
        except ValueError:
            logger.error(f"Unknown {sort_method=}")
            printer.lines(  # LATER: this as printer function of class.Enum...?
                header="Choose one of this sort arguments:",
                style="Danger",
                lines=[f"sort_method={m}" for m in self.Sort],
                title="TreeSelectorApp.Sort",
            )
        logger.info(f"Using {self.sort_method.value=}")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        root_identifier = self.sst_tree.identifier
        root_label: str = self.sst_tree.display_label

        self.original_labels[root_identifier] = root_label

        display: str = self.format_label(root_identifier, root_label)

        tree: MultiSelectTree = MultiSelectTree(
            label=display,
            data=root_identifier,
        )
        tree.root.expand()
        yield tree
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Select Branches or Single Nodes"

        tree: MultiSelectTree = self.query_one(MultiSelectTree)
        self.build_ui_tree(sst_node=self.sst_tree, current_tui_node=tree.root)

    def format_label(self, identifier: str, original_label: str) -> str:
        """Formats the text to visually indicate if a node is selected."""
        if identifier in self.selected_identifiers:
            return f"[bold green]◉[/bold green] {original_label}"
        return f"[dim]◯[/dim] {original_label}"

    def build_ui_tree(
        self, sst_node: SimpleTreeNode, current_tui_node: TreeNode[str]
    ) -> None:
        for sst_branch in sst_node.branches:
            identifier: str = sst_branch.identifier
            original_label: str = sst_branch.display_label

            # Keep track of original labels to cleanly format them later
            self.original_labels[identifier] = original_label

            display: str = self.format_label(identifier, original_label)

            next_tui_node: TreeNode[str] = current_tui_node.add(
                label=display,
                data=identifier,
                expand=True,
            )
            self.build_ui_tree(
                sst_node=sst_branch, current_tui_node=next_tui_node
            )

    def on_multi_select_tree_node_toggled(
        self, event: MultiSelectTree.NodeToggled
    ) -> None:
        """Fire when Spacebar is pressed"""

        if not (target_identifier := event.node.data):
            logger.debug(f"TTT Strange {event.node=} with {event.node.data=}")
            return  # TEST: when happens this?

        is_selecting = target_identifier not in self.selected_identifiers

        def update_node_and_children(ui_node: TreeNode):

            if not (node_id := ui_node.data):
                logger.debug(f"TTT Strange {ui_node=} with {ui_node.data=}")
                return  # TEST: when happens this?

            if is_selecting:
                self.selected_identifiers[node_id] = None
            else:
                # discard doesn't error if missing
                self.selected_identifiers.pop(node_id, None)

            ui_node.label = self.format_label(
                node_id, self.original_labels[node_id]
            )
            # Recursive down to select all sub-elements in folder
            for child in ui_node.children:
                update_node_and_children(child)

        update_node_and_children(event.node)

    def on_multi_select_tree_submitted(
        self, _event: MultiSelectTree.Submitted
    ) -> None:
        """Fired when Enter is pressed"""

        if self.selected_identifiers:
            result: list[str] = list(self.selected_identifiers.keys())
            if self.sort_method == self.Sort.ALPHABETIC:
                result.sort(
                    key=lambda x: self.original_labels.get(x, x).lower()
                )
            self.exit(result=result)
        else:
            tree: MultiSelectTree = self.query_one(MultiSelectTree)
            if tree.cursor_node and tree.cursor_node.data:
                # No Selection return identifier of current cursor position
                self.exit(result=[tree.cursor_node.data])
            else:
                self.exit(result=[])  # or nothing if nothing found there

    def action_quit_without_selection(self) -> None:
        """Close without result"""
        self.exit(result=[])
