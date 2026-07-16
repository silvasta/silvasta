"""
Compose Printer Essentials, Interchangeables and Optionals

- Dynamically assemble customized Printers with PrinterFactory
- Provide preconfigured default printer instance

"""

from typing import Any

__all__: list[str] = [
    "PrinterFactory",
    "printer",
]

from dataclasses import dataclass

from . import mixin
from .blueprint import Printer
from .root import PrinterCore


@dataclass(frozen=True)
class PrinterFactory:
    """Configure PrinterMixins and build composed classes"""

    core: type = PrinterCore
    # Essentials
    color: type = mixin.ColorMixin
    format: type = mixin.NormalizeMixin
    render: type = mixin.RenderMixin
    # Layout layers
    panel: type = mixin.PanelMixin
    header: type = mixin.HeaderMixin
    box: type = mixin.BoxMixin
    line: type = mixin.LineMixin
    table: type = mixin.TableMixin
    md: type = mixin.MarkdownMixin
    # Optionals
    tool: type | None = None
    emit: type | None = None

    def all_mixins(self) -> tuple[type | None, ...]:
        """Provide all attached member raw and unfiltered"""
        return (
            self.core,
            self.color,
            self.format,
            self.render,
            self.panel,
            self.header,
            self.box,
            self.line,
            self.table,
            self.md,
            self.tool,
            self.emit,
        )

    def mixins(self) -> tuple[type, ...]:
        """Provide all selected Mixins in a stable order"""
        return tuple(mixin for mixin in self.all_mixins() if mixin is not None)

    def _create_name(self, name="") -> str:
        return f"{name}Printer"

    def assemble(self, name="") -> type[Printer]:
        """Compose selected Mixins to Printer Class"""
        return type(self._create_name(name), self.mixins(), {})

    def construct(self, name="", **init_kwargs: Any) -> Printer:
        """Initialize Printer Class assembled from Mixins"""
        return self.assemble(name)(**init_kwargs)


printer: Printer = PrinterFactory().construct()
