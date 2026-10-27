"""
Connect all Parts and Release the Printer

-
"""

__all__: list[str] = [
    "PrinterLayouts2",
]


from typing import Unpack

from ...brick.field import FunctorField
from ...forge.view.factory import DtoFactory, dto_factory
from ...forge.view.render import DtoRenderHub
from ...port.color import Color
from ...port.event.dto import CliSpec, MarkdownDTO, MarkdownInput, PanelDTO
from ...port.link import portlink
from ...port.printer import PrintLayouts
from ._base import PrinterBase
from ._functors import (
    BoxPrintFunctor,
    ColoredHeaderInput,
    DipPrintFunctor,
    HeaderPrintFunctor,
    LinePrintFunctor,
    PanelPrintFunctor,
    TablePrintFunctor,
)


@portlink(PrintLayouts)
class PrinterLayouts2(PrinterBase):
    """Assemble DtoFactory, Render and many Presets"""

    def __init__(self, factory: DtoFactory = dto_factory, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dto: DtoFactory = factory
        self.render = DtoRenderHub(colors=self.colors)

    panel = FunctorField(PanelPrintFunctor)
    lines = FunctorField(LinePrintFunctor)
    box = FunctorField(BoxPrintFunctor)
    table = FunctorField(TablePrintFunctor)
    header = FunctorField(HeaderPrintFunctor)
    dip = FunctorField(DipPrintFunctor)

    def md(self, content: str, /, **kw: Unpack[MarkdownInput]) -> MarkdownDTO:
        return self(self.md(content, **kw))

    # -- High-Level Semantic Presets (Level 4) --
    # Work as 1-liner banners: printer.success("Done!")
    # Or titled content panels: printer.success("Done", "All 5 tasks completed")

    def success(
        self,
        title: str,
        *content: CliSpec,
        **kw: Unpack[ColoredHeaderInput],
    ) -> PanelDTO:
        return self.header(title, *content, color=Color.GREEN, **kw)

    def warn(
        self,
        title: str,
        *content: CliSpec,
        **kw: Unpack[ColoredHeaderInput],
    ) -> PanelDTO:
        return self.header(title, *content, color=Color.YELLOW, **kw)

    def danger(
        self,
        title: str,
        *content: CliSpec,
        **kw: Unpack[ColoredHeaderInput],
    ) -> PanelDTO:
        return self.header(title, *content, color=Color.RED, **kw)

    def special(
        self,
        title: str,
        *content: CliSpec,
        **kw: Unpack[ColoredHeaderInput],
    ) -> PanelDTO:
        return self.header(title, *content, color=Color.PURPLE, **kw)
