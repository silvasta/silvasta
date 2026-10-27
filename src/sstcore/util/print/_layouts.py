"""
Connect all Parts and Release the Printer

-
"""

__all__: list[str] = [
    "PrinterLayouts",
]


from typing import Any, Unpack

from ...brick.field import FunctorField
from ...forge.view.factory import DtoFactory, dto_factory
from ...forge.view.render import DtoRenderHub
from ...port._types import _Stringable
from ...port.color import Color
from ...port.event import dto
from ...port.link import portlink
from ...port.printer import PrintLayouts
from ._base import PrinterBase
from ._functors import (
    BoxPrintFunctor,
    DipPrintFunctor,
    HeaderPrintFunctor,
    LinePrintFunctor,
    TablePrintFunctor,
)


@portlink(PrintLayouts)
class PrinterLayouts(PrinterBase):
    """Assemble DtoFactory, RenderHub, PrintFunctors and many Presets"""

    line = FunctorField(LinePrintFunctor)
    lines = FunctorField(LinePrintFunctor)
    box = FunctorField(BoxPrintFunctor)
    table = FunctorField(TablePrintFunctor)
    header = FunctorField(HeaderPrintFunctor)
    dip = FunctorField(DipPrintFunctor)

    def __init__(self, factory: DtoFactory = dto_factory, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dto: DtoFactory = factory
        self.render = DtoRenderHub(colors=self.colors)

    def panel(
        self, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self(self.dto.panel(*content, **kw))

    def md(
        self, content: _Stringable, /, **kw: Unpack[dto.MarkdownInput]
    ) -> dto.MarkdownDTO:
        return self(self.dto.md(content, **kw))

    #  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def title(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.HeaderPresetInput],
    ) -> dto.PanelDTO:
        """Render Header Panel with `self.project_info` as default topic."""
        merged: dict[str, Any] = dict(kw)
        if not content:
            merged.setdefault("topic", self.project_info)
        else:
            merged.setdefault("header_topic", self.project_info)
        return self.header(title, *content, **merged)

    def success(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO:
        return self.header(title, *content, color=Color.GREEN, **kw)

    def warn(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO:
        return self.header(title, *content, color=Color.YELLOW, **kw)

    def danger(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO:
        return self.header(title, *content, color=Color.RED, **kw)

    def special(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO:
        return self.header(title, *content, color=Color.PURPLE, **kw)
