"""
The Printer - Fast and Beautiful Access to Rich Console!

Dynamiacally build the 'Printer' with optional Mixins.

- Define functions and types in Printer: Protocol
- Collect Mixins in PrinterFactory for assemble
- Expose pre-configured global printer: Printer

"""

__all__: list[str] = [
    "Printer",
    "PrinterFactory",
    "printer",
]


from .compose import PrinterFactory, printer
from .protocol import Printer
