"""
Transform DTO to RichRenderable

- CliDTO: Specialized for CLI
- LogDTO: Intended for Monitor

"""

__all__: list[str] = [
    "RenderMixin",
]

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

    def render_panel(self: Printer, dto: PanelDTO) -> RichRenderable:
        content: str = self.normalize(dto.text)
        content: str = self.color(content, dto.color)
        title: str | None = (  # TODO: color apply inside PanelDTO?
            # TASK: synchronize with internal layouts
            self.color(dto.title, "white")  # PARAM: color
            if dto.title
            else None
        )
        return Panel(
            renderable=content,
            title=title,
            title_align=dto.title_align,
            subtitle=dto.subtitle,
            border_style=dto.frame,
            padding=dto.padding,
            box=dto.box,
            expand=dto.expand,
        )

    def render_line(self: Printer, dto: LineDTO) -> RenderableType:
        text: str = dto.text if dto.text is not None else "─" * 40
        return self.color(text, dto.style)

    def render_rule(self: Printer, dto: RuleDTO) -> RichRenderable:
        return Rule(style=dto.style, characters=dto.char)

    def render_table(self: Printer, dto: TableDTO) -> RichRenderable:
        table = Table(style=dto.style)

        # LATER: color layout for header and side title,
        # together with ColorBox and Palette

        for header in dto.header:
            table.add_column(header)

        for row in dto.rows:
            prepared_row: list[str] = [self.normalize(value) for value in row]
            table.add_row(*prepared_row)

        return table

    def render_markdown(self: Printer, dto: MarkdownDTO) -> RenderableType:
        content: str = self.normalize(dto.text)
        if dto.header > 0:
            prefix = "#" * dto.header + " "
            return self.color(f"{prefix}{content}", dto.style)
        return self.color(content, dto.style)

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
