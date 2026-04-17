from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Tree

from silvasta.utils.simple_tree import SimpleTreeNode


class TreeSelectorApp(App[str]):
    """A transient app that displays a tree and returns the selected node."""

    # We return 'None' if the user cancels
    BINDINGS = [
        Binding("escape", "quit_without_selection", "Cancel"),
        Binding("q", "quit_without_selection", "Quit"),
    ]

    def __init__(self, tree_data: SimpleTreeNode, **kwargs):
        super().__init__(**kwargs)
        self.tree_data = tree_data

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        # The 'data' argument is the hidden payload we will return later
        tree: Tree[str] = Tree(self.tree_data.name, data=self.tree_data.name)
        tree.root.expand()
        yield tree
        yield Footer()

    def on_mount(self) -> None:
        """Populate the tree widget with our SimpleTreeNode data."""
        self.title = "Select a Node"
        self.sub_title = "Use arrows to navigate, Enter to select"

        tree = self.query_one(Tree)
        self.build_ui_tree(self.tree_data, tree.root)

    def build_ui_tree(self, node: SimpleTreeNode, ui_node) -> None:
        for child in node.next:
            node_payload: str = child.id if child.id else child.name

            new_ui_node = ui_node.add(
                child.name, data=node_payload, expand=True
            )
            self.build_ui_tree(child, new_ui_node)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Fired when the user hits Enter on a node."""
        if event.node.data:
            # self.exit() closes the app and returns the value to whoever called .run()
            self.exit(result=event.node.data)

    def action_quit_without_selection(self) -> None:
        # Exit returning None to indicate cancellation
        self.exit(result=None)
