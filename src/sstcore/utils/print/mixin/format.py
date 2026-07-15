import textwrap
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from loguru import logger
from rich.console import ConsoleRenderable, RichCast
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

from ....contract.cli import CliRenderable, PanelDTO, TableDTO
from ...log.inspect import debug_log_or_print
from ..base import BasePrinter


class FormatMixin(BasePrinter):
    """Ensure Input is printable"""

    @debug_log_or_print(anyway=False)
    def format(self, target: Any, indent: int = 0) -> Any:
        """Check Target type and return printable format"""

        # IMPORTANT: make switch to bypass __cli__ and execute __rich__
        if isinstance(target, CliRenderable):
            return self._render_dto(target.__cli__())

        if isinstance(target, (ConsoleRenderable, RichCast)):
            # If it has an indent and is already Rich object, wrap it in Padding
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
            self(f"table: {dto}")
            table = Table(title=dto.title, style=dto.style, show_header=True)
            headers: list[str] = dto.headers or (
                list(dto.data[0].keys()) if dto.data else []
            )
            # COLLECT: util to transform tabular data
            for col in headers:
                table.add_column(col)
            for row in dto.data:
                table.add_row(
                    *(str(row.get(col, "")) for col in headers)
                    if isinstance(row, dict)
                    else row
                )
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
