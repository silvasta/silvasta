"""
The Printer - Fast and Beautiful Access to Rich Console!

Dynamiacally build the 'Printer' with optional Mixins.

- Expose pre-configured global printer instance and factory function

"""

__all__: list[str] = [
    "printer",
    "Printer",
    "create_printer",
]

from typing import TYPE_CHECKING

from .base import BasePrinter
from .mixin.color import ColorMixin
from .mixin.format import FormatMixin
from .mixin.layout import LayoutMixin
from .mixin.tool import ToolMixin

# REFACTOR: simplify assembling!
# IDEA: move mixer to print.core or resolve completely


def create_printer(color=True, tool=True, format=True, layout=True):
    """Stack the selected Mixins and assemble the Printer class!"""

    # COLLECT: mixer pattern, apply where it makes sense:
    # - here? most likely at most issues with at most minimal gain...
    # - view! precisily mix the defaults for new classes (check risk first)
    # - registry, looks tempting but same risk as here

    chain: list = []

    if format:  # set False for risking crashes
        chain.append(FormatMixin)
    if color:  # set False for no colors (like the same as no printer)
        chain.append(ColorMixin)
    if layout:  # set False for no comfort
        chain.append(LayoutMixin)
    if tool:  # Actually this works standalone
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

# AI: assemble and init the printer here is in discussion to change...

printer: Printer = Printer()
