"""
Compose Printer Essentials, Interchangeables and Optionals

- Dynamically assemble customized Printers with PrinterFactory
- Provide preconfigured default printer instance

"""

__all__: list[str] = [
    "PrinterFactory",
    "printer",
]

from dataclasses import dataclass
from typing import Any

from rich.console import Console

from ..color import colorize
from ..view import ViewBuilder
from ..view.presets import printer_view_builder
from . import mixin
from .blueprint import Printer
from .root import PrinterCore

PrinterViewBuilder: ViewBuilder = printer_view_builder()


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
    # view
    view_spec: ViewBuilder | None = PrinterViewBuilder

    def all_mixins(self) -> tuple[type | None, ...]:
        """Provide all attached member raw and unfiltered"""
        return (
            self.emit,
            self.tool,
            #
            self.md,
            self.table,
            self.line,
            #
            self.box,
            self.header,
            self.panel,
            #
            self.render,
            self.color,
            self.format,
            #
            self.core,
        )

    def mixins(self) -> tuple[type, ...]:
        """Provide all selected Mixins in stable Order"""
        return tuple(mixin for mixin in self.all_mixins() if mixin is not None)

    def display(self) -> None:
        """Show all selected Mixins colorized in Order"""
        mixins: str = "\n".join(colorize.modules(m) for m in self.mixins())
        Console().print(mixins)

    def assemble(self, name="") -> type[Printer]:
        """Compose selected Mixins to Printer Class"""
        printer: type = type(self._create_name(name), self.mixins(), {})
        return self.view_spec.compose(printer) if self.view_spec else printer

    def _create_name(self, name="") -> str:
        return f"{name}Printer"

    def construct(self, name="", **init_kwargs: Any) -> Printer:
        """Initialize Printer Class assembled from Mixins"""
        return self.assemble(name)(**init_kwargs)


printer: Printer = PrinterFactory().construct("Sst")
