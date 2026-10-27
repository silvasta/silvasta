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

# AI_TASK: the final goal is: printer
# - resolve both versions to 1 resulting Printer

from ...port.link import portlink as _portlink
from ...port.printer import Print
from ._base import PrinterBase
from ._boxes import Boxes
from ._engine import PrinterCore
from ._layouts1 import PrinterLayouts1
from ._layouts2 import PrinterLayouts2


@_portlink(Print)
class Printer1(PrinterCore, PrinterLayouts1, PrinterBase):
    """The Final Composition"""


printer1 = Printer1()


@_portlink(Print)
class Printer2(PrinterCore, PrinterLayouts2, PrinterBase):
    """The Final Composition"""


printer2 = Printer2()
