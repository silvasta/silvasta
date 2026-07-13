"""
Log Monitor 2: Advanced JSONL & Plain-text Structured Tailer

Supports live colorized rendering, metadata expansion,
and deep CLI filtering for central development telemetry.
"""

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

from ...config import sst_config
from ...utils import PathGuard, printer

# Level styles mapped directly to theme configuration palette
LEVEL_STYLES = {
    "DEBUG": "dim cyan",
    "INFO": "bold white",
    "WARNING": "bold yellow",
    "ERROR": "bold red",
    "CRITICAL": "bold red on black",
    "SUCCESS": "bold green",
}


def log_monitor(
    log_path: Path | None = None,
    level: str | None = None,
    sender: str | None = None,
    search: str | None = None,
):
    """Show tail log display with optional structured filters"""
    log_file: Path = PathGuard.file(
        target=log_path or sst_config().settings.log.log_file,
        default_content="",
        raise_error=False,
    )

    # Normalize level values for comparison
    min_level_val = _level_weight(level) if level else 0

    try:
        launch_tail_log_console(
            log_file=log_file,
            min_level_val=min_level_val,
            sender_filter=sender,
            search_query=search,
        )
    except KeyboardInterrupt:
        printer.line("dashed")
        printer.warn("Log monitor tailing stopped")
        sys.exit(0)


def _level_weight(level_name: str) -> int:
    """Return numeric weight of level to allow threshold filtering"""
    weights = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
        "SUCCESS": 25,
    }
    return weights.get(level_name.upper(), 0)


def launch_tail_log_console(
    log_file: Path,
    min_level_val: int = 0,
    sender_filter: str | None = None,
    search_query: str | None = None,
):
    """Launch visual stream with parsed NDJSON formatting"""

    header_info = [
        f"File: [cyan]{PathGuard.relative(log_file, strict=False)}[/]",
    ]
    if min_level_val > 0:
        header_info.append(f"Level: [yellow]>= {min_level_val}[/]")
    if sender_filter:
        header_info.append(f"Sender: [magenta]{sender_filter}[/]")
    if search_query:
        header_info.append(f"Query: [green]'{search_query}'[/]")

    printer.title(
        header_info,
        title="Telemetry Monitor v2",
        title_align="right",
        frame="purple",
    )

    # Compile search filter ahead of time
    search_re = (
        re.compile(search_query, re.IGNORECASE) if search_query else None
    )

    # Begin tailing loop
    with open(log_file, encoding="utf-8") as f:
        f.seek(0, 2)  # Move cursor to end of file

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.05)  # Keep latency extremely low
                continue

            line_str = line.strip()
            if not line_str:
                continue

            # Process structured JSON line or legacy string line
            try:
                data = json.loads(line_str)
                process_json_line(
                    data, min_level_val, sender_filter, search_re
                )
            except json.JSONDecodeError:
                # Fallback to standard line styling if not raw JSON
                process_legacy_line(line_str, min_level_val, search_re)


def process_json_line(
    data: dict[str, Any],
    min_level_val: int,
    sender_filter: str | None,
    search_re: re.Pattern | None,
):
    """Parse, filter, and format an NDJSON log entry elegantly"""
    level = data.get("level", "INFO").upper()
    sender = data.get("sender") or data.get("extra", {}).get("sender")
    message = data.get("message", "")

    # 1. Filter Check: Level
    if _level_weight(level) < min_level_val:
        return

    # 2. Filter Check: Sender
    if sender_filter and (
        not sender or sender_filter.lower() not in sender.lower()
    ):
        return

    # 3. Filter Check: Search term
    if (
        search_re
        and not search_re.search(message)
        and not search_re.search(str(data))
    ):
        return

    # Extract time component (Standardize ISO format representation)
    raw_time = data.get("time", "")
    time_str = raw_time[11:19] if len(raw_time) > 19 else "Time Error"

    # Context path
    module = data.get("module", "")
    func = data.get("function", "")
    line_no = data.get("line", "")
    context = f"[dim]{module}.{func}:{line_no}[/dim]" if module else ""

    # Level Tag styling
    lvl_style = LEVEL_STYLES.get(level, "white")
    level_badge = f"[{lvl_style}]{level:<8}[/]"

    # Sender context representation
    sender_tag = f"([magenta]{sender}[/magenta])" if sender else ""

    # Assemble and write core output row
    printer.console.print(
        f"[green]{time_str}[/] | {level_badge} | {sender_tag} [bold]{message}[/]  {context}"
    )

    # Extract dynamic extras, LogDTO metrics or details
    excluded_keys = {
        "time",
        "level",
        "message",
        "module",
        "function",
        "line",
        "sender",
        "event_name",
    }
    meta_payload = {k: v for k, v in data.items() if k not in excluded_keys}

    if meta_payload:
        formatted_meta = []
        for key, value in meta_payload.items():
            val_str = (
                json.dumps(value, ensure_ascii=False)
                if isinstance(value, (dict, list))
                else str(value)
            )
            formatted_meta.append(f"[cyan]{key}[/]=[dim yellow]{val_str}[/]")

        # Output payload metadata in aligned sublevel
        printer.console.print(
            f"         └── [dim]context:[/] {' | '.join(formatted_meta)}"
        )


def process_legacy_line(
    line: str, min_level_val: int, search_re: re.Pattern | None
):
    """Parse regular unstructured log lines for backwards compatibility"""
    # Quick filter check for regex on raw log entries
    if search_re and not search_re.search(line):
        return

    # Crude level checking for legacy logs to keep output clean
    level = "INFO"
    style = "white"
    for lvl, stl in LEVEL_STYLES.items():
        if lvl in line:
            level = lvl
            style = stl
            break

    if _level_weight(level) < min_level_val:
        return

    printer(line, style=style)
