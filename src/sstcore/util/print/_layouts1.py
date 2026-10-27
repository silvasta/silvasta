"""
Connect all Parts and Release the Printer

-
"""

__all__: list[str] = [
    "PrinterLayouts1",
]

from typing import Unpack

from ...brick.field import FunctorField
from ...forge.view.factory import (
    CliDtoProducer,
    DtoFactory,
    LineDtoProducer,
    LogDtoProducer,
    MarkdownDtoProducer,
    PanelDtoProducer,
    TableDtoProducer,
    dto_factory,
)
from ...forge.view.factory._produce import (
    # REMOVE: this producer are not desired!
    BoxDtoProducer,
    HeaderDtoProducer,
    StatusDtoProducer,
)
from ...forge.view.render import DtoRenderHub
from ...port.color import Color, ColorArg
from ...port.event import dto
from ...port.link import portlink
from ...port.printer import PrintLayouts
from ._base import PrinterBase


@portlink(PrintLayouts)
class PrinterLayouts1(PrinterBase):
    """Assemble DtoFactory, Render and many Presets"""

    def __init__(self, factory: DtoFactory = dto_factory, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dto: DtoFactory = factory
        self.render = DtoRenderHub(colors=self.colors)

    log = FunctorField(LogDtoProducer)
    cli = FunctorField(CliDtoProducer)
    panel = FunctorField(PanelDtoProducer)
    md = FunctorField(MarkdownDtoProducer)
    line = FunctorField(LineDtoProducer)
    lines = FunctorField(LineDtoProducer)
    table = FunctorField(TableDtoProducer)

    # Tier 2: Structural Preset Functors
    box = FunctorField(BoxDtoProducer)
    header = FunctorField(
        HeaderDtoProducer  # AI: here some default_topic makes sense: Printer.project_info
    )

    # Tier 3: Semantic Status Preset Functors
    success = FunctorField(
        StatusDtoProducer,
        default_color=Color.GREEN,
        default_topic="SUCCESS",  # REMOVE: undesired default_topic! the color is intended for this Information!!
    )
    warn = FunctorField(
        StatusDtoProducer,
        default_color=Color.YELLOW,
        default_topic="WARNING",  # REMOVE: for all
    )
    danger = FunctorField(
        StatusDtoProducer, default_color=Color.RED, default_topic="DANGER"
    )
    special = FunctorField(
        StatusDtoProducer, default_color=Color.PURPLE, default_topic="SPECIAL"
    )
    info_box = FunctorField(
        StatusDtoProducer, default_color=Color.AZURE, default_topic="INFO"
    )

    def dip(  # IMPORTANT: this is for sure its own Functor!
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        color: ColorArg = Color.AZURE,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO:
        """Top-level shortcut for `printer.header.dip(head, text, ...)`."""
        return self.header.dip(head, text, *content, color=color, **kw)
