import textwrap
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from loguru import logger
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

from ....events.dto import LogDTO, PanelDTO, TableDTO
from ....events.protocol import CliRenderable
from ...log.inspect import debug_log_or_print
from ..base import BasePrinter


class FormatMixin(BasePrinter):
    """Ensure Input is printable"""

    # NEXT: check how to attach here the new __cli__ _render or render

    @debug_log_or_print(anyway=False)
    def format(self, target: Any, indent: int = 0) -> Any:
        """Check Target type and return printable format"""

        if isinstance(target, CliRenderable):
            return self._render_dto(target.__cli__())

        # If it has an indent and is already a Rich object, wrap it in Padding
        if hasattr(target, "__rich__") or hasattr(target, "__rich_console__"):
            return Padding(target, (0, 0, 0, indent)) if indent else target

        if isinstance(target, str):
            return self.indent(target, indent=indent)

        return self._format(target, indent=indent)

    def indent(self, target, indent=0) -> str:
        return (
            textwrap.indent(str(target), " " * indent)
            if indent
            else str(target)
        )

    # AI_TASK: format dispatches to here, here just dispatch by specific DTO,
    # either to sub functions or rendering maybe in color.colorize
    def _render_dto(self, dto: Any) -> Any:
        # TEST: just experimenting with some functions,
        # - so far nothing serious here
        if isinstance(dto, PanelDTO):
            lines = [f"[bold]{k}:[/bold] {v}" for k, v in dto.metrics.items()]
            rendered_lines = "\n".join(lines)
            return Panel(
                rendered_lines,
                title=f"[bold white]{dto.title}[/bold white]",
                subtitle=f"[dim]{dto.content}[/dim]",
                border_style=dto.frame,
            )
        if isinstance(dto, TableDTO):
            table = Table(title=dto.title, style=dto.style, show_header=True)
            for col in dto.columns:
                table.add_column(col)
            for row in dto.rows:
                table.add_row(*(str(cell) for cell in row))
            return table
        if isinstance(dto, LogDTO):  # REMOVE:
            # Formatted line output for basic messages
            color_map = {
                "INFO": "cyan",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold red",
            }
            col = color_map.get(dto.level.upper(), "white")
            return f"[{col}][{dto.level}][/] {dto.message}"
        return dto

    @singledispatchmethod
    def _format(self, target, indent=0) -> str:
        if self._log:
            logger.warning(f"Unknown format of {type(target)=}: {target=}")
        return self.indent(str(target), indent)

    # AI_QUESTION: is _format more than a Path colorizer or str(target) caster?

    @_format.register
    def _(self, target: list, indent=0) -> str:
        items: list[str] = [self._format(item, indent) for item in target]
        return "\n".join(items)

    @_format.register
    def _(self, target: Path, indent=0) -> str:
        """Make folder parts blue and file name white"""

        if target.is_dir():
            return self.indent(f"[blue]{target}/[/]", indent)

        if target.parent != Path("."):
            # LATER: adapt for relative paths, color files by type?
            return self.indent(
                f"[blue]{target.parent}/[/][white]{target.name}[/]"
            )

        return self.indent(target.name)
