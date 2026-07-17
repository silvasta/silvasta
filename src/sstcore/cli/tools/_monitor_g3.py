import json
import sys
import time
from datetime import datetime
from pathlib import Path

from ...config import sst_config
from ...utils import PathGuard, printer
from ...utils.parse import LogPatterns


def log_monitor(log_path: Path | None = None, level_filter: str | None = None):
    """Show tail log display, aware of both raw .log and structured .jsonl"""

    log_file: Path = PathGuard.file(
        target=log_path
        or sst_config().settings.log.log_file,  # Default to .log
        default_content="",
        raise_error=False,
    )

    try:
        launch_tail_log_console(log_file, level_filter)
    except KeyboardInterrupt:
        printer.warn("Log file tailing stopped by user")
        sys.exit(0)


def launch_tail_log_console(log_file: Path, level_filter: str | None = None):
    """Launch console with live log prints from file"""

    printer.title(
        [
            f"Tailing {printer._format(log_file)} ...",
            f"Mode: {log_file.suffix.upper()}",
        ],
        title="Loguru Smart Monitor",
        title_align="right",
        frame="purple",
    )

    is_json = log_file.suffix == ".jsonl"

    with open(log_file) as f:
        f.seek(0, 2)  # Move to end of file

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            line = line.strip()
            if not line:
                continue

            if is_json:
                _render_json_line(line, level_filter)
            else:
                _render_raw_line(line)


def _render_json_line(line: str, level_filter: str | None):
    """Parse NDJSON line and format it beautifully via Printer"""
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        printer(f"[dim red]Failed to parse JSON:[/] {line}")
        return

    # Basic filtering
    level = data.get("level", "INFO")
    if level_filter and level.upper() != level_filter.upper():
        return

    # Style mapping
    level_styles = {
        "DEBUG": "bold yellow",
        "INFO": "bold cyan",
        "WARNING": "bold magenta",
        "ERROR": "bold white on red",
        "SUCCESS": "bold green",
    }
    style = level_styles.get(level, "white")

    # Time parsing (shorten the ISO timestamp to HH:MM:SS)
    raw_time = data.get("time", "")
    try:
        # Assuming ISO format like: 2026-07-12T09:18:16.938955+02:00
        dt = datetime.fromisoformat(raw_time)
        time_str = dt.strftime("%H:%M:%S")
    except ValueError:
        time_str = raw_time[:8] if raw_time else "00:00:00"

    # Core log line construction
    module = data.get("module", "unknown")
    func = data.get("function", "")
    msg = data.get("message", "")

    # We use Rich markup tags directly in the string for the printer
    formatted_line = (
        f"[dim]{time_str}[/] | "
        f"[{style}]{level: <8}[/] | "
        f"[dim cyan]{module}:{func}[/] - "
        f"{msg}"
    )

    printer(formatted_line)

    # --- The "Smart" part: Handling LogDTO Extras & Metrics ---
    # We extract keys that aren't the standard loguru keys
    standard_keys = {"time", "level", "message", "module", "function", "line"}
    extra_data = {k: v for k, v in data.items() if k not in standard_keys}

    if extra_data:
        # If there are metrics or custom DTO payloads, we use your layout mixins
        # to draw a nice indented box or rule under the log line.
        metrics = extra_data.pop("metrics", None)

        if metrics:
            # Just an example of using your LayoutMixin
            printer.mini_box(
                f"[bold cyan]Metrics:[/] {metrics}", frame="cyan", mode="down"
            )

        if extra_data:
            # Print remaining extra context slightly dimmed and indented
            # You can pass dicts directly if your Printer formats them, or format as string
            printer(f"  [dim]↳ Context: {extra_data}[/]")


def _render_raw_line(line: str):
    """Fallback for old .log files"""

    match line:
        case LogPatterns.DEBUG:
            style = "bold yellow"
        case LogPatterns.INFO:
            style = "bold white"
        case LogPatterns.WARNING:
            style = "bold magenta"
        case LogPatterns.ERROR:
            style = "bold red"
        case LogPatterns.SUCCESS:
            style = "bold green"
        case _:
            style = None

    printer(line, style=style)
