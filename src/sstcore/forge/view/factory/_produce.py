"""
Prepare Functors, 1 per DTO

- add optional safe mode
- handle stacked functions

"""

__all__: list[str] = [
    "LogDtoProducer",
    "CliDtoProducer",
    "PanelDtoProducer",
    "MarkdownDtoProducer",
    "LineDtoProducer",
    "TableDtoProducer",
]

from collections.abc import Sequence
from typing import Any, Unpack

from ....port._types import event_types as _dto
from ....port.event.dto import (
    CliData,
    CliDTO,
    CliSpec,
    DtoNames,
    EventDTO,
    LineDTO,
    LineSpec,
    LogDTO,
    LogSpec,
    MarkdownDTO,
    MarkdownSpec,
    PanelDTO,
    PanelSpec,
    TableSpec,
)
from ....port.represent import Stringable
from ...func import SafeFunctor
from ._table import TableViewDTO


class DtoProducer[DTO: EventDTO = EventDTO](SafeFunctor[..., DTO]):
    """Assemble the DTO - handle variations"""

    dto_name: DtoNames

    def __init__(self, registry: _dto.Map[type[DTO]], **kwargs):  # DTO:Any
        self._registry: _dto.Map[type[DTO]] = registry
        super().__init__(**kwargs)

    @property
    def dto_cls(self) -> type[DTO]:
        return self._registry[self.dto_name]


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDtoProducer(DtoProducer[LogDTO]):
    dto_name: DtoNames = "log"

    def call(self, message: str, /, **kw: Unpack[LogSpec]) -> LogDTO:
        return self.dto_cls.create(message=message, **kw)

    # __call__ = call


class CliDtoProducer(DtoProducer[CliDTO]):
    dto_name: DtoNames = "cli"

    def call(
        self, content: Sequence[CliData], /, **kw: Unpack[CliSpec]
    ) -> CliDTO:
        return self.dto_cls.create(content, **kw)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PanelDtoProducer(DtoProducer[PanelDTO]):
    dto_name: DtoNames = "panel"

    def call(self, *content: CliData, **kw: Unpack[PanelSpec]) -> PanelDTO:
        return self.dto_cls.create(*content, **kw)


class MarkdownDtoProducer(DtoProducer[MarkdownDTO]):
    """Create ..."""

    dto_name: DtoNames = "markdown"

    def call(
        self, content: Stringable, /, **kw: Unpack[MarkdownSpec]
    ) -> MarkdownDTO:
        return self.dto_cls.create(content, **kw)


class LineDtoProducer(DtoProducer[LineDTO]):
    """Create ..."""

    dto_name: DtoNames = "line"

    def call(self, *content: CliData, **kw: Unpack[LineSpec]) -> LineDTO:
        return self.dto_cls.create(content, **kw)


class TableDtoProducer(DtoProducer[TableViewDTO]):
    dto_name: DtoNames = "table"

    def call(
        self, content: tuple[tuple[CliData]], /, **kw: Unpack[TableSpec]
    ) -> TableViewDTO:
        return self.dto_cls.create(content, **kw)

    def from_cols(
        self, cols: dict[str, Sequence[Any]], *, corner: str = ""
    ) -> TableViewDTO:
        return self.dto_cls.table_from_cols(cols, corner=corner)
