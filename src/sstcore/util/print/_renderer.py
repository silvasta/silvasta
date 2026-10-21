"""
Prepare Functors, 1 per DTO

- add optional safe mode
- handle stacked functions

"""

from ...forge.func import SafeFunctor
from ...port.event.dto import (
    CliDTO,
    DtoNames,
    EventDTO,
    GroupDTO,
    LineDTO,
    LogDTO,
    MarkdownDTO,
    PanelDTO,
    TableDTO,
)


class DtoRenderer(SafeFunctor):
    """Visualize the DTO - handle variations"""

    dto_name: DtoNames
    base_dto: type[EventDTO]


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDTORenderer(DtoRenderer):
    """Render ..."""

    dto_name: DtoNames = "log"
    base_dto: type[LogDTO] = LogDTO

    def call(self) -> LogDTO:
        """Main Layout"""


class CliDTORenderer(DtoRenderer):
    """Render ..."""

    dto_name: DtoNames = "cli"
    base_dto: type[CliDTO] = CliDTO

    def call(self) -> CliDTO:
        """Main Layout"""


class PanelDTORenderer(DtoRenderer):
    """Render ..."""

    dto_name: DtoNames = "panel"
    base_dto: type[PanelDTO] = PanelDTO

    def call(self) -> PanelDTO:
        """Main Layout"""


class MarkdownDTORenderer(DtoRenderer):
    """Render ..."""

    dto_name: DtoNames = "markdown"
    base_dto: type[MarkdownDTO] = MarkdownDTO

    def call(self) -> MarkdownDTO:
        """Main Layout"""


class GroupDTORenderer(DtoRenderer):
    """Render ..."""

    dto_name: DtoNames = "group"
    base_dto: type[GroupDTO] = GroupDTO

    def call(self) -> GroupDTO:
        """Main Layout"""


class LineDTORenderer(DtoRenderer):
    """Render ..."""

    dto_name: DtoNames = "line"
    base_dto: type[LineDTO] = LineDTO

    def call(self) -> LineDTO:
        """Main Layout"""


class TableDTORenderer(DtoRenderer):
    """Render ..."""

    dto_name: DtoNames = "table"
    base_dto: type[TableDTO] = TableDTO

    def call(self) -> TableDTO:
        """Main Layout"""
