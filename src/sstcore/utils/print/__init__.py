"""
The Printer - Fast and Beautiful Access to rich.Console!

This submodule provides a configurable 'Printer' class constructed dynamiacally
using optional mixins (Format, Color, Layout, Tool) and the simple Colorbox.
It exposes a pre-configured global `printer` instance or the factory function.
"""  # LATER: write less condensed

__all__: list[str] = [
    "printer",
    "Printer",
    "create_printer",
    "ColorBox",
]

from typing import TYPE_CHECKING

from .base import BasePrinter
from .mixin.color import ColorMixin
from .mixin.format import FormatMixin  # AI: this one is main target
from .mixin.layout import LayoutMixin
from .mixin.tool import ToolMixin


def create_printer(color=True, tool=True, format=True, layout=True):
    """Stack the selected Mixins and assemble the Printer class!"""
    chain: list = []

    if format:
        # AI: for the others, the pipeline makes more or less sense,
        # here I assume the format is needed but with another structure
        chain.append(FormatMixin)
        # TODO: check the role of FormatMixin,
        # is it maybe just a more universal util that is called?
    if color:
        chain.append(ColorMixin)
    if layout:
        chain.append(LayoutMixin)
    if tool:
        chain.append(ToolMixin)

    chain.append(BasePrinter)

    return type("Printer", tuple(chain), {})


_DynamicPrinter = create_printer()

if TYPE_CHECKING:

    class Printer(
        FormatMixin, ColorMixin, LayoutMixin, ToolMixin, BasePrinter
    ):
        """Type-hinting stub for perfect autocomplete."""

        pass
else:
    # At runtime, bind the dynamic class to the name 'Printer'
    Printer = _DynamicPrinter

printer: Printer = Printer()
