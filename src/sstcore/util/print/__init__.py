"""
The Printer - Fast and Beautiful Access to Rich Console!

Dynamiacally build the 'Printer' with optional Mixins.

- Define functions and types in Printer: Protocol
- Collect Mixins in PrinterFactory and assemble
- Expose pre-configured global printer: Printer

"""

__all__: list[str] = [
    "printer",
    "Printer",
    "Boxes",
]

from ...port.link import portlink as _portlink
from ...port.printer import Print
from ._base import PrinterBase
from ._boxes import Boxes
from ._engine import PrinterCore
from ._layouts import PrinterLayouts


@_portlink(Print)
class Printer(PrinterCore, PrinterLayouts, PrinterBase):
    """The Final Composition"""


printer = Printer()
