"""
Log Monitor 2

Structured JSONL viewer

"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.text import Text

from ...config import sst_config
from ...utils import PathGuard
from ...utils.print import printer


def log_monitor(
    log_path: Path | None = None,
    levels: list[str] | None = None,
    simple: bool = False,
):
    """Main entry point for the log monitor."""
    log_file = PathGuard.file(
        target=log_path
        or sst_config().settings.log.log_file.with_suffix(".jsonl"),
        default_content="",
        raise_error=False,
    )

    if simple or not log_file.suffix == ".jsonl":
        _run_simple_tail(log_file)
    else:
        _run_structured_monitor(log_file, levels=levels or [])


def _run_simple_tail(log_file: Path):
    """Fallback to old behavior (colored lines)."""
    from .monitor import launch_tail_log_console

    launch_tail_log_console(log_file)


# ============================================================
# Structured JSONL Monitor (Recommended)
# ============================================================


def _run_structured_monitor(log_file: Path, levels: list[str]):
    """Modern structured monitor using Rich + live tailing."""
    console = Console()

    printer.title(
        [f"Tailing {printer._format(log_file)} (structured)"],
        title="Log Monitor 2",
        frame="purple",
    )

    # Read from end
    with open(log_file, encoding="utf-8") as f:
        f.seek(0, 2)

        try:
            while True:
                if not (line := f.readline()):
                    time.sleep(0.15)
                    continue

                record = _parse_json_line(line)
                if not record:
                    continue

                if levels and record.get("level", "").upper() not in levels:
                    continue

                _render_log_line(console, record)

        except KeyboardInterrupt:
            printer.warn("Log monitoring stopped")
            return


def _parse_json_line(line: str) -> dict[str, Any] | None:
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {"level": "RAW", "message": line}


def _render_log_line(console: Console, record: dict[str, Any]):
    """Render one structured log entry nicely."""
    level = record.get("level", "INFO").upper()
    time_str = record.get("time", "")[:19].replace("T", " ")
    module = record.get("module", "")
    message = record.get("message", "")
    metrics = record.get("metrics", {})
    extra = record.get("extra", {})

    # Color by level
    level_style = {
        "DEBUG": "dim yellow",
        "INFO": "white",
        "WARNING": "yellow",
        "ERROR": "bold red",
        "SUCCESS": "green",
    }.get(level, "white")

    # Build main line
    parts = [
        Text(time_str, style="dim"),
        Text(f" {level:<8}", style=level_style),
    ]

    if module:
        parts.append(Text(f" {module}", style="cyan"))

    parts.append(Text(f"  {message}", style="white"))

    console.print(*parts)

    # Show metrics/extra compactly if present
    if metrics or extra:
        detail = []
        if metrics:
            detail.append(f"metrics={metrics}")
        if extra:
            detail.append(f"extra={extra}")

        console.print(" " * 12 + " ".join(detail), style="dim")
