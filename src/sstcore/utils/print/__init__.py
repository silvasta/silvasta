from typing import TYPE_CHECKING

from .base import BasePrinter
from .mixin.color import ColorMixin
from .mixin.format import FormatMixin
from .mixin.layout import LayoutMixin
from .mixin.tool import ToolMixin
from .stylebox import ColorBox


def create_printer(color=True, tool=True, format=True, layout=True):
    chain: list = []

    if format:
        chain.append(FormatMixin)
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

__all__: list = [
    "printer",
    "Printer",
    "create_printer",
    "ColorBox",
]
