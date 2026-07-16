from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from sstcore.contract.log import LogDTO

from ....contract.cli import (
    CliDTO,
    LineDTO,
    MarkdownDTO,
    PanelDTO,
    RuleDTO,
    TableDTO,
)
from ....contract.external import RenderableType, RichRenderable
from ..blueprint import Printer


class RenderMixin:
    def render(self: Printer, dto: CliDTO) -> RichRenderable:
        """Centralized render dispatcher using pattern matching."""

        match dto:
            case PanelDTO() as panel:
                return self.render_panel(panel)
            case LineDTO() as line:
                return self.render_line(line)
            case RuleDTO() as rule:
                return self.render_rule(rule)
            case TableDTO() as table:
                return self.render_table(table)
            case MarkdownDTO() as markdown:
                return self.render_markdown(markdown)
            case LogDTO() as log:
                return self.render_log(log)
            case _:
                raise TypeError(f"No render strategy implemented for {dto}")

    def render_panel(self: Printer, panel: PanelDTO) -> RichRenderable:
        content: str = self.normalize(panel.text)
        content: str = self.color(content, panel.color)
        title: str | None = (
            self.color(panel.title, "white") if panel.title else None
        )
        return Panel(
            renderable=content,
            title=title,
            title_align=panel.title_align,
            subtitle=panel.subtitle,
            border_style=panel.frame,
            padding=panel.padding,
            box=panel.box,
            expand=panel.expand,
        )

    def render_line(self: Printer, line: LineDTO) -> RenderableType:
        text: str = line.text if line.text is not None else "─" * 40
        return self.color(text, line.style)

    def render_rule(self: Printer, rule: RuleDTO) -> RichRenderable:
        return Rule(style=rule.style, characters=rule.char)

    def render_table(self: Printer, table: TableDTO) -> RichRenderable:
        rich_table = Table()
        if table.headers:
            for header in table.headers:
                rich_table.add_column(header)
        for row in table.data:
            row_data = row.values() if isinstance(row, dict) else row
            rich_table.add_row(*(str(item) for item in row_data))
        return rich_table

    def render_markdown(
        self: Printer, markdown: MarkdownDTO
    ) -> RenderableType:
        content = self.normalize(markdown.text)
        if markdown.header > 0:
            prefix = "#" * markdown.header + " "
            return self.color(f"{prefix}{content}", markdown.style)
        return self.color(content, markdown.style)

    def render_log(self: Printer, log: LogDTO) -> RichRenderable:
        _log_tests = [  # TESTING:
            _render_log_3,
            _render_log_1,
            _render_log_2,
        ]
        return _log_tests[0](log)


def _render_log_1(log: LogDTO) -> RichRenderable:
    """For the NDJSON log monitor (and optionally for console)."""
    color = {"ERROR": "red", "WARN": "yellow", "INFO": "cyan"}.get(
        log.level.upper(), "blue"
    )
    text = f"[{color}]{log.level:5}[/] {log.message}"
    if log.metrics or log.extra:
        text += f"  [dim]{log.metrics | log.extra}[/]"
    return Text.from_markup(text)


def _render_log_2(log: LogDTO) -> RichRenderable:
    """Render dynamic logs  in a clean format"""
    level_colors = {
        "DEBUG": "dim cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red",
    }
    color = level_colors.get(log.level.upper(), "white")

    # Build colored log message header
    header = Text()
    header.append(f"[{log.level.upper():<8}]", style=color)
    header.append(
        f" {log.message}",
        style="bold white" if log.level in ("ERROR", "CRITICAL") else "white",
    )

    # If clean log without extra attributes, return early as plain text layout
    if not log.metrics and not log.extra:
        return header

    # Render extra details as an aligned Branch Tree for highly professional logs
    tree = Tree(header, guide_style="dim white")
    if log.metrics:
        metrics_branch = tree.add("[cyan]Metrics[/cyan]")
        for key, val in log.metrics.items():
            metrics_branch.add(
                f"[dim cyan]{key}:[/dim cyan] [white]{val}[/white]"
            )

    if log.extra:
        extra_branch = tree.add("[magenta]Context[/magenta]")
        for key, val in log.extra.items():
            extra_branch.add(
                f"[dim magenta]{key}:[/dim magenta] [white]{val}[/white]"
            )

    return tree


def _render_log_3(log: LogDTO) -> RichRenderable:
    """Render a Log DTO beautifully for console monitoring."""

    # Color code based on log level
    level_colors = {
        "DEBUG": "dim white",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red",
    }
    style = level_colors.get(log.level.upper(), "white")

    # Construct a Rich Text object
    text = Text()
    text.append(f"[{log.level.upper():^8}] ", style=style)
    text.append(f"{log.message} ", style="white")

    # Append metrics/extras cleanly if they exist
    if log.metrics or log.extra:
        metadata = {**log.metrics, **log.extra}
        meta_str = " ".join(f"{k}={v}" for k, v in metadata.items())
        text.append(f"({meta_str})", style="dim italic")

    return text
