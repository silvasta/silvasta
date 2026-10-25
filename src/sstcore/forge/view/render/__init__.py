"""
Create Global RenderHub that visualizes all EventDTOs

- Specialize Functors for EventDTO rendering
  - Update EventDTO.registry if needed
- Mount them reliably with DescriporFields

"""

__all__: list[str] = [
    "DtoRenderHub",
    #
    "LogDtoProducer",
    "CliDtoProducer",
    "PanelDtoProducer",
    "MarkdownDtoProducer",
    "LineDtoProducer",
    "TableDtoProducer",
]


from ....brick.field._functor import FunctorField
from ....port.color import ColorBox
from ....port.event import dto
from ....port.event.dto import EventDTO
from ....port.represent import CliRenderable
from ._renderer import (
    CliDtoRenderer,
    DtoRenderer,
    LineDtoRenderer,
    LogDtoRenderer,
    MarkdownDtoRenderer,
    PanelDtoRenderer,
    TableDtoRenderer,
)


class DtoRenderHub:
    """Mount all DTO Renderers and provide unified dispatch."""

    log = FunctorField(LogDtoRenderer)
    cli = FunctorField(CliDtoRenderer)
    panel = FunctorField(PanelDtoRenderer)
    md = FunctorField(MarkdownDtoRenderer)
    line = FunctorField(LineDtoRenderer)
    table = FunctorField(TableDtoRenderer)

    def __init__(self, colors: ColorBox) -> None:
        self.colors: ColorBox = colors  # CHECK: just Colors?
        self._dispatch: dict[str, DtoRenderer[EventDTO]] = {
            "log": self.log,
            "cli": self.cli,
            "panel": self.panel,
            "markdown": self.md,
            "line": self.line,
            "table": self.table,
        }

    def __call__(self, target: dto.EventDTO) -> CliRenderable:
        renderer: DtoRenderer[EventDTO] | None = self._dispatch.get(target.name)
        if not renderer:
            raise TypeError(f"No renderer registered for DTO '{target.name}'")
        return renderer(target)
