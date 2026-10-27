"""
Create Global RenderHub that visualizes all EventDTOs

- Specialize Functors for EventDTO rendering
  - Update EventDTO.registry if needed
- Mount them reliably with DescriporFields

"""

__all__: list[str] = [
    "DtoRenderHub",
    "DtoVisualizer",
    "LogDtoVisualizer",
    "CliDtoVisualizer",
    "PanelDtoVisualizer",
    "MarkdownDtoVisualizer",
    "LineDtoVisualizer",
    "TableDtoVisualizer",
]


from ....brick.field._functor import FunctorField
from ....port.color import ColorBox
from ....port.event import dto
from ....port.event.dto import EventDTO
from ....port.represent import Richable
from ._visualize import (
    CliDtoVisualizer,
    DtoVisualizer,
    LineDtoVisualizer,
    LogDtoVisualizer,
    MarkdownDtoVisualizer,
    PanelDtoVisualizer,
    TableDtoVisualizer,
)


class DtoRenderHub:
    """Mount all DTO Visualizers and provide unified dispatch."""

    log = FunctorField(LogDtoVisualizer)
    cli = FunctorField(CliDtoVisualizer)
    panel = FunctorField(PanelDtoVisualizer)
    md = FunctorField(MarkdownDtoVisualizer)
    line = FunctorField(LineDtoVisualizer)
    table = FunctorField(TableDtoVisualizer)

    def __init__(self, colors: ColorBox) -> None:
        self.colors: ColorBox = colors  # CHECK: just Colors?
        self._dispatch: dict[str, DtoVisualizer[EventDTO]] = {
            "log": self.log,
            "cli": self.cli,
            "panel": self.panel,
            "markdown": self.md,
            "line": self.line,
            "table": self.table,
        }

    def __call__(self, target: dto.EventDTO) -> Richable:
        renderer: DtoVisualizer[EventDTO] | None = self._dispatch.get(
            target.name
        )
        if not renderer:
            raise TypeError(f"No renderer registered for DTO '{target.name}'")
        return renderer(target)
