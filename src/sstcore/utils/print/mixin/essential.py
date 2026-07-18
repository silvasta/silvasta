"""
Ensure pipeline arguments

- normalize: from Any type to stable string
- colorize: attach color and color combinations

Note:
  - still under construction
  - concept will change
"""

__all__: list[str] = [
    "ColorBox",
    "NormalizeMixin",
]
import textwrap
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from ....contract.cli import LineDTO
from ...color import ColorBox, colorize
from ..blueprint import Printer


class NormalizeMixin:
    @singledispatchmethod
    def normalize(self: Printer, target: Any, indent: int = 0) -> str:
        """Fallback: stringify and apply optional indentation."""
        text = str(target)
        return textwrap.indent(text, " " * indent) if indent else text

    @normalize.register(list)
    def _(self: Printer, target: list, indent: int = 0) -> str:
        """Flatten lists recursively and maintain indentation."""
        items: list[str] = [
            self.normalize(item, indent=indent) for item in target
        ]
        return "\n".join(items)

    @normalize.register(Path)
    def _(self: Printer, target: Path, indent: int = 0) -> str:
        """Delegate Path coloring to the external colorize utility."""
        text: str = colorize.path(target)
        return textwrap.indent(text, " " * indent) if indent else text


class ColorMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def white(self: Printer, target: Any) -> None:
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
