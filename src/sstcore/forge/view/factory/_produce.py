"""
Prepare Functors, 1 per DTO

- add optional safe mode
- handle stacked functions

"""

from src.sstcore.brick.field._strategy import StrategyField

__all__: list[str] = [
    "LogDtoProducer",
    "CliDtoProducer",
    "PanelDtoProducer",
    "MarkdownDtoProducer",
    "LineDtoProducer",
    "TableDtoProducer",
]

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Self, Unpack

from ....brick.field._functor import MountableFunctor
from ....port import functorial
from ....port.event import dto
from ....port.link import portlink
from ....port.represent import Stringable
from ...func import SafeFunctor
from ._table import TableViewDTO


@portlink(MountableFunctor)
@portlink(functorial.Functorial)
class DtoProducer[DTO: dto.EventDTO = dto.EventDTO](SafeFunctor[..., DTO]):
    """Assemble the DTO - handle variations"""

    dto_name: dto.DtoNames

    def __init__(self, registry: dto.DtoTable[DTO], **kwargs):  # DTO:Any
        self._registry: dto.DtoTable[DTO] = registry
        super().__init__(**kwargs)

    @classmethod
    def __mount__(cls, host: Any, name: str) -> Self:
        # IDEA: put this on BaseFunctor with just:
        # return cls(*args,**kwargs)
        # -> any Functor can then be mounted, use it with FuncorField!
        return cls(registry=host._registry, name=name)

    @property
    def dto_cls(self) -> type[DTO]:
        return self._registry[self.dto_name]


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@portlink(MountableFunctor)
class LogDtoProducer(DtoProducer[dto.LogDTO]):
    dto_name: dto.DtoNames = "log"

    # @StrategyField  # REMOVE: after implementation finished
    def call(self, message: str, /, **kw: Unpack[dto.LogSpec]) -> dto.LogDTO:
        return self.dto_cls.create(message=message, **kw)

    if TYPE_CHECKING:
        __call__ = call


@portlink(functorial.Functorial)
@portlink(MountableFunctor)
class CliDtoProducer(DtoProducer[dto.CliDTO]):
    dto_name: dto.DtoNames = "cli"

    def __call__(  # IDEA:
        self, content: Sequence[dto.CliData], /, **kw: Unpack[dto.CliSpec]
    ) -> dto.CliDTO:
        return self.dto_cls.create(content, **kw)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@portlink(MountableFunctor)
class PanelDtoProducer(DtoProducer[dto.PanelDTO]):
    dto_name: dto.DtoNames = "panel"

    @StrategyField  # REMOVE: after implementation finished
    def call(
        self, *content: dto.CliData, **kw: Unpack[dto.PanelSpec]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(*content, **kw)

    if TYPE_CHECKING:
        __call__ = call


@portlink(MountableFunctor)
class MarkdownDtoProducer(DtoProducer[dto.MarkdownDTO]):
    """Create ..."""

    dto_name: dto.DtoNames = "markdown"

    @StrategyField  # REMOVE: after implementation finished
    def call(
        self, content: Stringable, /, **kw: Unpack[dto.MarkdownSpec]
    ) -> dto.MarkdownDTO:
        return self.dto_cls.create(content, **kw)


class LineDtoProducer(DtoProducer[dto.LineDTO]):
    """Create ..."""

    dto_name: dto.DtoNames = "line"

    @StrategyField  # REMOVE: after implementation finished
    def call(
        self, *content: dto.CliData, **kw: Unpack[dto.LineSpec]
    ) -> dto.LineDTO:
        return self.dto_cls.create(content, **kw)


class TableDtoProducer(DtoProducer[TableViewDTO]):
    dto_name: dto.DtoNames = "table"

    @StrategyField  # REMOVE: after implementation finished
    def call(
        self,
        content: tuple[tuple[dto.CliData]],
        /,
        **kw: Unpack[dto.TableSpec],
    ) -> TableViewDTO:
        return self.dto_cls.create(content, **kw)

    def from_cols(
        self, cols: dict[str, Sequence[Any]], *, corner: str = ""
    ) -> TableViewDTO:
        return self.dto_cls.table_from_cols(cols, corner=corner)
