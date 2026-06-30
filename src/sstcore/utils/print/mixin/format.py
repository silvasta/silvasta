import textwrap
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from loguru import logger
from rich.padding import Padding

from ...log.inspect import debug_log_or_print
from ..base import BasePrinter


class FormatMixin(BasePrinter):
    """Ensure Input is printable"""

    @debug_log_or_print(anyway=False)
    def format(self, target: Any, indent=0) -> Any:
        """Check Target type and return printable format"""

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

    @singledispatchmethod
    def _format(self, target, indent=0) -> str:
        if self._log:
            logger.warning(f"Unknown format of {type(target)=}: {target=}")
        return self.indent(str(target), indent)

    @_format.register
    def _(self, target: Path, indent=0) -> str:
        """Make folder parts blue and file name white"""

        if target.is_dir():
            return self.indent(f"[blue]{target}/[/]", indent)

        if target.parent != Path("."):
            return self.indent(  # LATER: color files by type?
                f"[blue]{target.parent}/[/][white]{target.name}[/]"
                # LATER: fix for relative paths called from different location
            )

        return self.indent(target.name)

    @_format.register
    def _(self, target: list, indent=0) -> str:
        items: list[str] = [self._format(item, indent) for item in target]
        return "\n".join(items)
