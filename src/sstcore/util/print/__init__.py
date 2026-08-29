"""
The Printer - Fast and Beautiful Access to Rich Console!

Dynamiacally build the 'Printer' with optional Mixins.

- Define functions and types in Printer: Protocol
- Collect Mixins in PrinterFactory and assemble
- Expose pre-configured global printer: Printer

"""

__all__: list[str] = [
    "box",
    "printer",
]


from . import _box as box
from ._compose import printer
