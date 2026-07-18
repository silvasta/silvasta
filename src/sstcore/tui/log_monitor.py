import json
import time
from collections.abc import Callable
from pathlib import Path

from rich.console import RenderableType
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    OptionList,
    Static,
)

from ..contract.log import LogDTO

PREDEFINED_CATCHES: dict[str, Callable[[LogDTO], bool]] = {
    "🌐 All Logs": lambda dto: True,  # <--- Add this line
    "🔥 All Errors": lambda dto: dto.level in ("ERROR", "CRITICAL"),
    "💾 DB Timeouts": lambda dto: (
        "timeout" in dto.message.lower()
        and dto.extra.get("source") == "database"
    ),
    "👤 Auth Failures": lambda dto: dto.metrics.get("auth_status") == "failed",
    "⚡ High Latency (>500ms)": lambda dto: (
        dto.metrics.get("response_time_ms", 0) > 500
    ),
}


class LogMonitorApp(App):
    """A Textual App to monitor ndjson log files dynamically."""

    CSS = """
    #sidebar {
        width: 20%;
        border-right: solid green;
    }
    #stream-pane {
        width: 45%;
        border-right: solid cyan;
    }
    #right-pane {
        width: 35%;
        padding: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear_logs", "Clear Buffer"),
        ("e", "toggle_errors", "Toggle Errors Only"),
    ]

    def __init__(
        self,
        log_file: Path,
        render_func: Callable[[LogDTO], RenderableType],
        max_buffer: int = 5000,  # Increased for exploring history
        tail: bool = False,  # Flag to determine live tailing
    ):
        super().__init__()
        self.log_file = log_file
        self.render_func = render_func
        self.max_buffer = max_buffer
        # TODO: tailing/running?
        self.is_live_tailing = tail

        self.log_buffer: list[LogDTO] = []
        self.search_term: str = ""
        self.errors_only: bool = False

        self._running = True
        self.active_catch_name: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            # 1. The Watchers Sidebar
            with Vertical(id="sidebar"):
                yield Static("🔎 Catches", classes="header")
                yield OptionList(*PREDEFINED_CATCHES.keys(), id="catch-list")

            # 2. The Main Stream
            with Vertical(id="stream-pane"):
                yield Input(
                    placeholder="Search current view...", id="search-bar"
                )
                yield DataTable(id="log-table", cursor_type="row")

            # 3. The Microscope
            with Vertical(id="right-pane"):
                yield Static("Select an event...", id="detail-view")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Level", "Message", "Extras")

        self.process_log_file()

    @work(thread=True)
    def process_log_file(self) -> None:
        """Background thread to read existing logs and optionally tail new ones."""
        if not self.log_file or not self.log_file.exists():
            self.call_from_thread(
                self.notify,
                f"File not found: {self.log_file}",
                severity="error",
            )
            return

        with open(self.log_file, encoding="utf-8") as f:
            # --- PHASE 1: Rapidly ingest existing file ---
            for line in f:
                if not self._running:
                    break
                self._parse_and_buffer(line)

            # Update the UI *once* after bulk loading
            self.call_from_thread(self.refresh_log_table)
            self.call_from_thread(
                self.notify,
                "Finished loading existing logs.",
                severity="information",
            )

            # --- PHASE 2: Live tailing (if enabled) ---
            if self.is_live_tailing:
                while self._running:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue

                    # For live tailing, we can update the UI line-by-line
                    dto = self._parse_and_buffer(line)
                    if dto:
                        self.call_from_thread(self._live_update_ui, dto)

    def _parse_and_buffer(self, line: str) -> LogDTO | None:
        """Parse a line, add it to the buffer, and return the DTO."""
        line = line.strip()
        if not line:
            return None

        try:
            data = json.loads(line)
            dto = LogDTO(
                message=data.get("message", ""),
                level=data.get("level", "INFO"),
                metrics=data.get("metrics", {}),
                extra=data.get("extra", {}),
            )

            self.log_buffer.append(dto)
            if len(self.log_buffer) > self.max_buffer:
                self.log_buffer.pop(0)

            return dto
        except json.JSONDecodeError:
            return None

    @on(DataTable.RowSelected)
    def display_log_details(self, event: DataTable.RowSelected) -> None:
        """Fires when you hit Enter or double-click a row."""
        # Find the selected DTO in our buffer using the row key
        selected_id = event.row_key.value
        selected_dto = next(
            (d for d in self.log_buffer if str(id(d)) == selected_id), None
        )

        if selected_dto:
            detail_view = self.query_one("#detail-view", Static)
            # Call your rich tree renderer! (e.g., _render_log_2)
            rendered_rich_tree = self.render_func(selected_dto)
            detail_view.update(rendered_rich_tree)

    def _matches_filter(self, dto: LogDTO) -> bool:
        """Updated to respect the active catch."""
        # 1. Check predefined catch
        if self.active_catch_name:
            catch_func = PREDEFINED_CATCHES[self.active_catch_name]
            if not catch_func(dto):
                return False

        # 2. Check search bar
        if self.search_term:
            search_target = f"{dto.message} {dto.level}".lower()
            if self.search_term not in search_target:
                return False

        return True

    @on(OptionList.OptionSelected, "#catch-list")
    def apply_catch(self, event: OptionList.OptionSelected) -> None:
        """Fires when you click a predefined catch in the sidebar."""
        selected_catch = event.option.prompt

        # Reset if "All Logs" is clicked, OR if the user clicks the active filter again
        if (
            selected_catch == "🌐 All Logs"
            or selected_catch == self.active_catch_name
        ):
            self.active_catch_name = None
            self.notify("Showing all logs")
            # Visually reset the OptionList selection to the top
            self.query_one("#catch-list", OptionList).highlighted = 0
        else:
            self.active_catch_name = selected_catch
            self.notify(f"Filtering by: {self.active_catch_name}")

        # Repopulate the table with the new filter applied
        self.refresh_log_table()

    def _add_row_to_table(self, dto: LogDTO) -> None:
        """Helper to format and add a single row to the DataTable."""
        table = self.query_one("#log-table", DataTable)

        level_color = {
            "ERROR": "red",
            "WARNING": "yellow",
            "WARN": "yellow",
        }.get(dto.level.upper(), "cyan")
        level_cell = f"[{level_color}]{dto.level}[/]"
        has_extra = "📈" if (dto.metrics or dto.extra) else ""

        table.add_row(level_cell, dto.message, has_extra, key=str(id(dto)))
        # Optional: Auto-scroll to the bottom if live tailing
        table.move_cursor(row=table.row_count - 1)

    def _live_update_ui(self, dto: LogDTO) -> None:
        """Called by the background worker to add a row dynamically."""
        if self._matches_filter(dto):
            self._add_row_to_table(dto)

    def refresh_log_table(self) -> None:
        """Clear the DataTable and rewrite matching entries from buffer."""
        table = self.query_one("#log-table", DataTable)
        table.clear()

        for dto in self.log_buffer:
            if self._matches_filter(dto):
                self._add_row_to_table(dto)

    @on(Input.Changed, "#search-bar")
    def update_search(self, event: Input.Changed) -> None:
        self.search_term = event.value.lower()
        self.refresh_log_table()

    def action_toggle_errors(self) -> None:
        self.errors_only = not self.errors_only
        self.notify(f"Errors only: {'ON' if self.errors_only else 'OFF'}")
        self.refresh_log_table()

    def action_clear_logs(self) -> None:
        self.log_buffer.clear()
        self.refresh_log_table()

    def on_unmount(self) -> None:
        """Ensure the background worker thread dies gracefully."""
        self._running = False
