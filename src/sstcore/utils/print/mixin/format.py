from enum import Enum
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from rich.console import ConsoleRenderable

from ...log.inspect import debug_log_or_print
from ..base import BasePrinter


class FormatMixin(BasePrinter):
    def __call__(self, target, *args, **kwargs):
        """Rich console print, printer.mute(): switch to regular print"""

        match self.modus:
            case self.Modus.RICH:
                super().__call__(self._format(target), *args, **kwargs)

            case self.Modus.STANDARD:
                print(args[0] or "something went wrong...")

            case self.Modus.NULL:
                pass

    @debug_log_or_print(anyway=False)
    def panel(self, target: Any | list[Any], **kwargs):
        if "frame" in kwargs:
            kwargs["border_style"] = kwargs.pop("frame")

        super().panel(self._format(target), **kwargs)

    @singledispatchmethod
    def _format(self, target) -> str:
        # logger.warning(f"Unknown format of {type(target)=}: {target=}")
        return str(target)

    @_format.register
    def _(self, target: str):  # LATER: any modification?
        """Let regular String just pass"""
        return target

    @_format.register
    def _(self, target: BaseModel):  # LATER: any modification?
        """Let regular String just pass"""
        return target

    @_format.register
    def _(self, target: ConsoleRenderable):
        """Let Default Rich objects just pass"""
        return target

    @_format.register
    def _(self, target: dict | Enum) -> str:
        return str(target)

    # REMOVE: after test
    # @_format.register
    # def _(self, target: Enum) -> str:
    #     return str(target)

    @_format.register
    def _(self, target: list | tuple) -> str:
        # LATER: fix format acrobatic
        items: list[str] = [str(self._format(item)) for item in target]
        return "\n".join(items)

    @_format.register
    # LATER: fix for relative paths called from different location
    def _(self, target: Path) -> str:  # LATER: color files by type?
        target = Path(target)
        if target.is_dir():
            return f"[blue]{target}/[/]"
        if target.parent != Path("."):  # TODO: color as arg
            return f"[blue]{target.parent}/[/]{target.name}"
        return target.name
