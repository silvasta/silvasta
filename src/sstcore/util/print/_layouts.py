"""
Connect all Parts and Release the Printer

-
"""

__all__: list[str] = [
    "PrinterLayouts",
]

from typing import Unpack

from ...forge.view.factory import DtoFactory, dto_factory
from ...forge.view.render import DtoRenderHub
from ...port.color import Color
from ...port.event import dto
from ...port.link import portlink
from ...port.printer import PrintLayouts
from ._base import PrinterBase
from ._boxes import Boxes


@portlink(PrintLayouts)
class PrinterLayouts(PrinterBase):
    """Assemble DtoFactory, Render and many Presets"""

    def __init__(self, factory: DtoFactory = dto_factory, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dto: DtoFactory = factory
        self.render = DtoRenderHub(colors=self.colors)

    def panel(
        self, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self(self.dto.panel(*content, **kw))

    def md(
        self, content: str, /, **kw: Unpack[dto.MarkdownInput]
    ) -> dto.MarkdownDTO:
        return self(self.dto.md(content, **kw))

    def lines(
        self, *content: dto.CliSpec, **kw: Unpack[dto.LineInput]
    ) -> dto.LineDTO:
        return self(self.dto.line(*content, **kw))

    def table(
        self, content: dto._Grid, /, **kw: Unpack[dto.TableInput]
    ) -> dto.TableDTO:
        return self(self.dto.table(content, **kw))

    def header(
        self, title: str, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self.panel(*content, title=title, **kw)

    def box(
        self,
        *content: dto.CliSpec,
        box: Boxes = Boxes.OPEN,
        **kw: Unpack[dto.PanelInput],
    ) -> dto.PanelDTO:
        return self.panel(*content, box=box, **kw)

    #  LINE: -- Below are rendered from Panel -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def success(
        self, title: str, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self.panel(*content, title=title, color=Color.GREEN, **kw)

    def warn(
        self, title: str, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self.panel(*content, title=title, color=Color.YELLOW, **kw)

    def danger(
        self, title: str, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self.panel(*content, title=title, color=Color.RED, **kw)
