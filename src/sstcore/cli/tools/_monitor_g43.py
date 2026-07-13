import json
import sys
import time
from pathlib import Path
from typing import Any

from ...config import sst_config
from ...utils import PathGuard, printer
from .monitor import launch_tail_log_console


def log_monitor(
    log_path: Path | None = None,
    level: str | None = None,
    grep: str | None = None,
    max_extra: int = 5,
):
    """Tail either .log or .jsonl. Structured JSONL gets nice rendering."""
    log_file = PathGuard.file(
        target=log_path
        or sst_config().settings.log.log_file.with_suffix(".jsonl"),
        default_content="",
        raise_error=False,
    )

    if log_file.suffix == ".jsonl":
        launch_jsonl_monitor(
            log_file, level=level, grep=grep, max_extra=max_extra
        )
    else:
        launch_tail_log_console(log_file)  # keep old behavior


def launch_jsonl_monitor(
    log_file: Path, level: str | None, grep: str | None, max_extra: int
):
    printer.title(
        [f"Tailing {printer._format(log_file)} ..."],
        title="Loguru JSONL Monitor",
        title_align="right",
        frame="purple",
    )

    try:
        with open(log_file) as f:
            f.seek(0, 2)
            while True:
                if not (line := f.readline().strip()):
                    time.sleep(0.08)
                    continue

                try:
                    rec: dict[str, Any] = json.loads(line)
                except json.JSONDecodeError:
                    printer(line)  # fallback
                    continue

                if level and rec.get("level", "").upper() != level.upper():
                    continue
                if grep and grep.lower() not in str(rec).lower():
                    continue

                _render_json_record(rec, max_extra)
    except KeyboardInterrupt:
        printer.warn("JSONL tail stopped")
        sys.exit(0)


def _render_json_record(rec: dict[str, Any], max_extra: int):
    level = rec.get("level", "INFO").upper()
    style = {
        "DEBUG": "yellow",
        "INFO": "white",
        "WARNING": "magenta",
        "ERROR": "red",
        "SUCCESS": "green",
    }.get(level, "white")

    header = (
        f"[bold {style}]{level:<8}[/] "
        f"[cyan]{rec.get('time', '')}[/] "
        f"{rec.get('module', '')}:{rec.get('function', '')}"
    )

    body = rec.get("message", "")
    extra = {
        k: v
        for k, v in rec.items()
        if k not in {"time", "level", "message", "module", "function", "line"}
    }

    if extra:
        shown = dict(list(extra.items())[:max_extra])
        body += "\n" + str(shown)
        if len(extra) > max_extra:
            body += f" … (+{len(extra) - max_extra})"

    printer.panel(
        body,
        title=header,
        frame=style,
        title_align="left",
        expand=False,
    )


# INFO: keep the original launch_tail_log_console(...) unchanged
