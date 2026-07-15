from .base import BasePrinter
from .mixin.color import ColorMixin
from .mixin.emit import EmitMixin
from .mixin.format import FormatMixin
from .mixin.layout import LayoutMixin
from .mixin.tool import ToolMixin


# 1. The Standard Local Printer (No Bus Integration)
class ConsolePrinter(
    ToolMixin,  # Calls layout methods
    LayoutMixin,  # Calls core __call__ and panel
    ColorMixin,  # Modifies strings
    FormatMixin,  # Modifies objects
    BasePrinter,  # Executes output
):
    """Standard terminal printer with full layout capabilities."""

    pass


# 2. The Event-Driven Printer
class SystemPrinter(
    EmitMixin,  # intercepts calls -> sends DTOs
    ConsolePrinter,  # inherits all the standard capabilities as fallbacks
):
    """Event-bus connected printer that intercepts outputs as DTOs."""

    pass


# 3. Instantiate the global singleton
printer = SystemPrinter()
