from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label, ListItem, ListView


class SelectableItem(ListItem):
    """A custom ListItem that holds its identifier and formats its own label."""

    def __init__(self, label: str, identifier: str) -> None:
        super().__init__()
        self.label_text: str = label
        self.identifier: str = identifier
        self.is_selected: bool = False

    def compose(self) -> ComposeResult:
        # Yield a Label that we can easily update later
        yield Label(self.format_label())

    def format_label(self) -> str:
        if self.is_selected:
            return f"[bold green]◉[/bold green] {self.label_text}"
        return f"[dim]◯[/dim] {self.label_text}"

    def update_display(self) -> None:
        """Refresh the Label text based on selection state."""
        self.query_one(Label).update(self.format_label())


class ListSelectorApp(App[list]):
    """A transient app that displays a flat list and returns the selected item(s)."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("space", "toggle_select", "Select Item"),
        Binding("enter", "submit", "Submit Selection"),
        Binding("escape", "quit_without_selection", "Cancel"),
        Binding("q", "quit_without_selection", "Quit"),
    ]

    def __init__(
        self, items: list | set | dict, multi_select: bool = False, **kwargs
    ):
        super().__init__(**kwargs)
        self.multi_select: bool = multi_select
        self.selected_identifiers: set = set()

        # Normalize inputs: dicts use keys as IDs and values as labels.
        # Lists/Sets use the item as both ID and label.
        if isinstance(items, dict):
            self.items: dict[str, str] = {
                str(k): str(v) for k, v in items.items()
            }
        else:
            self.items = {str(item): str(item) for item in items}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        list_items = [
            SelectableItem(label=label, identifier=identifier)
            for identifier, label in self.items.items()
        ]
        yield ListView(*list_items, id="selection_list")
        yield Footer()

    def on_mount(self) -> None:
        mode_text = "Multi-Select" if self.multi_select else "Single-Select"
        self.title = f"Select Item(s) [{mode_text}]"
        # self.sub_title = "j/k: Navigate | Space: Toggle | Enter: Submit" # REMOVE: after test of automatic labels

    # --- Actions ---
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Fired natively by ListView when Enter is pressed."""
        self.action_submit()

    def action_cursor_down(self) -> None:
        """Vim 'j': Route down navigation to the ListView."""
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        """Vim 'k': Route up navigation to the ListView."""
        self.query_one(ListView).action_cursor_up()

    def action_toggle_select(self) -> None:
        """Spacebar: Toggle the selection state of the highlighted item."""
        list_view = self.query_one(ListView)
        item = list_view.highlighted_child

        if not isinstance(item, SelectableItem):
            return

        if not self.multi_select:
            # Single-select mode: clear all other selections first
            self.selected_identifiers.clear()
            for child in list_view.children:
                if isinstance(child, SelectableItem) and child is not item:
                    child.is_selected = False
                    child.update_display()

        # Toggle the targeted item
        item.is_selected = not item.is_selected

        if item.is_selected:
            self.selected_identifiers.add(item.identifier)
        else:
            self.selected_identifiers.discard(item.identifier)

        item.update_display()

    def action_submit(self) -> None:
        """Enter: Return selections, falling back to the highlighted item if none selected."""
        if self.selected_identifiers:
            self.exit(result=list(self.selected_identifiers))
        else:
            # Fallback (same as your original logic)
            list_view = self.query_one(ListView)
            item = list_view.highlighted_child
            if isinstance(item, SelectableItem):
                self.exit(result=[item.identifier])
            else:
                self.exit(result=[])

    def action_quit_without_selection(self) -> None:
        """Escape/q: Close without result"""
        self.exit(result=[])
