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


from ._assemble import Printer, printer
from ._boxes import Boxes
