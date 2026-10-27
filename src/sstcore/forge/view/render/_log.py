"""
Visualize the Log DTO for different Levels of Inspection

- Prepare for CLI and as well LogMonitor

"""

from rich.text import Text
from rich.tree import Tree

from ....port.event.dto import LogDTO
from ....util.parse._match import LogMatcher

# INFO: probably drop LogViewDTO, LogDTO.metainfo might be better
# class LogViewDTO(LogDTO, name="log"):
#     """Extend features for rendering"""
#     def metainfo(self) -> dict[str, Any]:
#         return {**self.extra, **self.metrics}


def render_log(log: LogDTO, select=0):
    """Test different Log renderings until final version is found"""
    _log_renderings = [
        _render_log_2,
        _render_log_3,
        _render_log_1,
    ]
    return _log_renderings[select](log)


def _match_color(log: LogDTO) -> str:
    return LogMatcher(log.level.upper()) or "white"


def _render_log_1(log: LogDTO):
    """For the NDJSON log monitor (and optionally for console)."""
    # LATER: fix with colorbox
    text = f"[{_match_color(log)}]{log.level:5}[/] {log.message}"
    if metainfo := log.metainfo():
        text += f"  [dim]{metainfo}[/]"
    return Text.from_markup(text)


def _render_log_2(log: LogDTO):
    """Render Logs by Level and with Extras/Metrics as Tree"""

    header = Text()
    header.append(f"[{log.level.upper():<8}]", style=_match_color(log))
    header.append(
        f" {log.message}",
        style="bold white" if log.level in ("ERROR", "CRITICAL") else "white",
    )
    if not log.metainfo():
        return header

    tree = Tree(header, guide_style="dim white")

    if log.metrics:
        metrics_branch = tree.add("[cyan]Metrics[/cyan]")
        for key, val in log.metrics.items():
            metrics_branch.add(
                f"[dim cyan]{key}:[/dim cyan] [white]{val}[/white]"
            )

    # TODO: looks nice beside of markup, fix with colorbox and test the trees

    if log.extra:
        extra_branch = tree.add("[magenta]Context[/magenta]")
        for key, val in log.extra.items():
            extra_branch.add(
                f"[dim magenta]{key}:[/dim magenta] [white]{val}[/white]"
            )

    return tree


def _render_log_3(log: LogDTO):
    """Render a Log DTO beautifully for console monitoring."""

    text = Text()
    text.append(f"[{log.level.upper():^8}] ", style=_match_color(log))
    text.append(f"{log.message} ", style="white")

    if metadata := log.metainfo():
        meta_str = " ".join(f"{k}={v}" for k, v in metadata.items())
        text.append(f"({meta_str})", style="dim italic")

    return text
