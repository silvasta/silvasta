"""
Compose Printer Essentials, Interchangeables and Optionals

- Dynamically assemble customized Printers with PrintComposer
- Provide preconfigured default printer instance

"""

__all__: list[str] = [
    "PrintComposer",
    "printer",
]

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from rich.console import Console

from ...brick.color import colorize
from ...brick.view import view
from ...port.printer import PrintCore
from ...port.shape import Composer
from . import _mixins
from ._engine import PrinterCore


@dataclass(frozen=True)
class PrintComposer[PrinT: PrintCore]:
    """Configure PrinterMixins and build composed classes"""

    core: type = PrinterCore
    # Essentials
    color: type = _mixins.ColorMixin
    format: type = _mixins.NormalizeMixin
    render: type = _mixins.RenderMixin
    # Layout layers
    panel: type = _mixins.PanelMixin
    header: type = _mixins.HeaderMixin
    box: type = _mixins.BoxMixin
    line: type = _mixins.LineMixin
    table: type = _mixins.TableMixin
    md: type = _mixins.MarkdownMixin
    # Optionals
    tool: type | None = None

    def all_mixins(self) -> tuple[type | None, ...]:
        """Provide all attached member raw and unfiltered"""
        return (
            self.tool,
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

    def mix_name(self, name="") -> str:
        return f"{name}Printer" if name else "PrintBase"

    def display(self) -> None:
        """Show all selected Mixins colorized in Order"""
        # EXTRACT:
        mixins: str = "\n".join(colorize.modules(m) for m in self.mixins())
        Console().print(mixins)

    def build(
        self,
        name="",
        format_name=True,
        extras: dict | None = None,
        *,
        mixins: tuple[type, ...] = (),
        _prepend: bool = True,
    ) -> PrinT:
        """Assemble selected Mixins to ViewBase"""
        cls_name: str = self.mix_name(name) if format_name else name or "View"
        bases: tuple[type, ...] = self.mixins() + mixins
        new_cls: type = type(cls_name, bases, extras or {})

        return cast(typ=PrinT, val=new_cls)


printer = PrintComposer().build(mixins=tuple(view.printer.build()))

if TYPE_CHECKING:
    _instance_check: Composer = PrintComposer()
    _class_check: type[Composer] = PrintComposer
