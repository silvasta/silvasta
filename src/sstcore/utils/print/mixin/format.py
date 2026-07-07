import textwrap
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from loguru import logger
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

from ....events.dto import PanelDTO, TableDTO
from ....events.protocol import CliRenderable
from ...log.inspect import debug_log_or_print
from ..base import BasePrinter


class FormatMixin(BasePrinter):
    """Ensure Input is printable"""

    @debug_log_or_print(anyway=False)
    def format(self, target: Any, indent: int = 0) -> Any:
        """Check Target type and return printable format"""

        if isinstance(target, CliRenderable):  # AI: here is an easy dispatch
            return self._render_dto(target.__cli__())

        # If it has an indent and is already a Rich object, wrap it in Padding
        if hasattr(target, "__rich__") or hasattr(target, "__rich_console__"):
            return Padding(target, (0, 0, 0, indent)) if indent else target

        if isinstance(target, str):
            return self.indent(target, indent=indent)

        return self._format(target, indent=indent)

    def _render_dto(self, dto: Any) -> Any:  # NEXT: proper __cli__ renderings

        if isinstance(dto, PanelDTO):  # WARN: dummy function
            lines = [f"[bold]{k}:[/bold] {v}" for k, v in dto.metrics.items()]
            rendered_lines = "\n".join(lines)
            return Panel(
                rendered_lines,
                title=f"[bold white]{dto.title}[/bold white]",
                subtitle=f"[dim]{dto.content}[/dim]",
                border_style=dto.frame,
            )
        if isinstance(dto, TableDTO):  # WARN: dummy function
            table = Table(title=dto.title, style=dto.style, show_header=True)
            for col in dto.columns:
                table.add_column(col)
            for row in dto.rows:
                table.add_row(*(str(cell) for cell in row))
            return table

        return dto

    def indent(self, target, indent=0) -> str:
        return (
            textwrap.indent(str(target), " " * indent)
            if indent
            else str(target)
        )

    @singledispatchmethod
    def _format(self, target, indent=0) -> str:
        if self._log:
            logger.warning(f"Unknown format of {type(target)=}: {target=}")
        return self.indent(str(target), indent)

    # TASK: check if _format is more than a Path colorizer or string caster
    # - otherwise move Path dispatch to color.colorize
    # - and just process the list somehow elegant

    @_format.register
    def _(self, target: list, indent=0) -> str:
        # WARN: why use _format here, works only for Path, rest -> str
        # for example a list of __cli__ or __rich__ will end up gray...
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
