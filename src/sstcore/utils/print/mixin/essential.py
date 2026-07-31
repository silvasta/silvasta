"""
Ensure pipeline arguments

- normalize: from Any type to stable string
- colorize: attach color and color combinations

Note:
  - still under construction
  - concept will change
"""

from pydantic import BaseModel

__all__: list[str] = [
    "ColorBox",
    "NormalizeMixin",
]
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from rich.console import ConsoleRenderable, RichCast

from ....format.color import ColorBox, colorize
from ....port import LineDTO
from ..blueprint import Printer


class NormalizeMixin:
    @singledispatchmethod
    def normalize(self: Printer, target: Any) -> str:  # TODO:-> RenderableType
        """Fallback: unknown target to str"""
        return str(target)

    @normalize.register(ConsoleRenderable | RichCast | str | BaseModel)
    def _(self: Printer, target):
        """Don't touch already ready objects"""
        return target

    @normalize.register(list)
    def _(self: Printer, target: list) -> str:
        """Flatten lists recursively and maintain indentation."""
        items: list[str] = [self.normalize(item) for item in target]
        return "\n".join(items)

    @normalize.register(Path)
    def _(self: Printer, target: Path) -> str:
        """Delegate Path coloring to the external colorize utility."""
        return colorize.path(target)


class ColorMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # AI: here how the ColorBox arrives
        self.color_box = ColorBox()

    @property
    def _cb(self) -> ColorBox:
        """Provide quick access to attached ColorBox"""
        return self.color_box

    @property
    def project_info(self: Printer) -> str:
        """Style the top right title of printer.title Panel"""
        name: str = self._cb.cyan(self.project_name)
        return f"{name} v{self.project_version}"

    def color(self, text: str, color: str | None = None) -> str:
        """Apply color and predefined style attribute (bold,...)"""
        return self.color_box(text, color) if text else ""

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Colors, how to apply them on any function?
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    # AI: this part is from the previous color mixin, as it in total where 4 and not 10
    # - meaning somewhen this stuff should be moved out of essentials

    def white(self: Printer, target: Any) -> None:
        # AI_FOCUS: here is exactly not how I want to assign colors
        # - the ColorBox needs a function (probably a property) that provides dot accesses colors,
        #   even if they are strings, maybe with some dataclass and magic methods or a StrEnum,
        #   maybe even some str inheritance hack
        self(LineDTO.from_call(target=target, style="white"))

    def blue(self: Printer, target: Any) -> None:
        self(LineDTO.from_call(target=target, style="blue"))

    def red(self: Printer, target: Any) -> None:
        self(LineDTO.from_call(target=target, style="red"))

    def green(self: Printer, target: Any) -> None:
        self(LineDTO.from_call(target=target, style="green"))

    def cyan(self: Printer, target: Any) -> None:
        self(LineDTO.from_call(target=target, style="cyan"))

    def magenta(self: Printer, target: Any) -> None:
        self(LineDTO.from_call(target=target, style="magenta"))

    def yellow(self: Printer, target: Any) -> None:
        self(LineDTO.from_call(target=target, style="yellow"))

    def black(self: Printer, target: Any) -> None:
        self(LineDTO.from_call(target=target, style="black"))
