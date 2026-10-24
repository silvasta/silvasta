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
from typing import Any, Self, Unpack

from ....port import functorial
from ....port.event import dto
from ....port.link import portlink
from ....port.represent import Stringable
from ...func import SafeFunctor
from ._table import TableViewDTO


@portlink(functorial.MountableFunctor)
class DtoProducer[DTO: dto.EventDTO = dto.EventDTO](SafeFunctor[..., DTO]):
    """Assemble the DTO - handle variations"""

    dto_name: dto.DtoNames

    def __init__(self, registry: dto.DtoTable[DTO], **kwargs):  # DTO:Any
        self._registry: dto.DtoTable[DTO] = registry
        super().__init__(**kwargs)

    @property
    def dto_cls(self) -> type[DTO]:
        return self._registry[self.dto_name]

    @classmethod
    def __mount__(cls, host: Any, /, *, name: str = "", **kwargs: Any) -> Self:
        return cls(registry=host._registry, name=name, **kwargs)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@portlink(functorial.MountableFunctor)
class LogDtoProducer(DtoProducer[dto.LogDTO]):
    dto_name: dto.DtoNames = "log"

    def __call__(
        self, message: str, /, **kw: Unpack[dto.LogInput]
    ) -> dto.LogDTO:
        return self.dto_cls.create(message=message, **kw)


@portlink(functorial.MountableFunctor)
class CliDtoProducer(DtoProducer[dto.CliDTO]):
    dto_name: dto.DtoNames = "cli"

    def __call__(
        self, content: Sequence[dto.CliSpec], /, **kw: Unpack[dto.CliInput]
    ) -> dto.CliDTO:
        return self.dto_cls.create(content, **kw)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@portlink(functorial.MountableFunctor)
class PanelDtoProducer(DtoProducer[dto.PanelDTO]):
    dto_name: dto.DtoNames = "panel"

    def __call__(
        self, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(*content, **kw)


@portlink(functorial.MountableFunctor)
class MarkdownDtoProducer(DtoProducer[dto.MarkdownDTO]):
    dto_name: dto.DtoNames = "markdown"

    def __call__(
        self, content: Stringable, /, **kw: Unpack[dto.MarkdownInput]
    ) -> dto.MarkdownDTO:
        return self.dto_cls.create(content, **kw)


@portlink(functorial.MountableFunctor)
class LineDtoProducer(DtoProducer[dto.LineDTO]):
    dto_name: dto.DtoNames = "line"

    def __call__(
        self, *content: dto.CliSpec, **kw: Unpack[dto.LineInput]
    ) -> dto.LineDTO:
        return self.dto_cls.create(content, **kw)


@portlink(functorial.MountableFunctor)
class TableDtoProducer(DtoProducer[TableViewDTO]):
    dto_name: dto.DtoNames = "table"

    def __call__(
        self,
        content: dto._Grid,
        /,
        **kw: Unpack[dto.TableInput],
    ) -> TableViewDTO:
        return self.dto_cls.create(content, **kw)

    # TODO: remaining methods (from forge.view.factory._table)
    def from_cols(
        self, cols: dict[str, Sequence[Any]], *, corner: str = ""
    ) -> TableViewDTO:
        return self.dto_cls.table_from_cols(cols, corner=corner)
