"""
Prepare Functors, 1 per DTO

- add optional safe mode
- handle stacked functions

"""

from ....port.event.dto import (
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
from ...func import SafeFunctor


class DtoProducer(SafeFunctor):
    """Assemble the DTO - handle variations"""

    dto_name: DtoNames
    base_dto: type[EventDTO]


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDTOProducer(DtoProducer):
    """Create ..."""

    dto_name: DtoNames = "log"
    base_dto: type[LogDTO] = LogDTO

    def call(self) -> LogDTO:
        """Main CTOR"""


class CliDTOProducer(DtoProducer):
    """Create ..."""

    dto_name: DtoNames = "cli"
    base_dto: type[CliDTO] = CliDTO

    def call(self) -> CliDTO:
        """Main CTOR"""


class PanelDTOProducer(DtoProducer):
    """Create ..."""

    dto_name: DtoNames = "panel"
    base_dto: type[PanelDTO] = PanelDTO

    def call(self) -> PanelDTO:
        """Main CTOR"""


class MarkdownDTOProducer(DtoProducer):
    """Create ..."""

    dto_name: DtoNames = "markdown"
    base_dto: type[MarkdownDTO] = MarkdownDTO

    def call(self) -> MarkdownDTO:
        """Main CTOR"""


class GroupDTOProducer(DtoProducer):
    """Create ..."""

    dto_name: DtoNames = "group"
    base_dto: type[GroupDTO] = GroupDTO

    def call(self) -> GroupDTO:
        """Main CTOR"""


class LineDTOProducer(DtoProducer):
    """Create ..."""

    dto_name: DtoNames = "line"
    base_dto: type[LineDTO] = LineDTO

    def call(self) -> LineDTO:
        """Main CTOR"""


class TableDTOProducer(DtoProducer):
    """Create ..."""

    dto_name: DtoNames = "table"
    base_dto: type[TableDTO] = TableDTO

    def call(self) -> TableDTO:
        """Main CTOR"""
