"""
Prepare Functors, 1 per DTO

- add optional safe mode
- handle stacked functions

"""

__all__: list[str] = [
    "DtoProducer",
    "LogDtoProducer",
    "CliDtoProducer",
    "PanelDtoProducer",
    "MarkdownDtoProducer",
    "LineDtoProducer",
    "TableDtoProducer",
]

from collections.abc import Mapping, Sequence
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


#  LINE: -- Log and Cli Base -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDtoProducer(DtoProducer[dto.LogDTO]):
    dto_name: dto.DtoNames = "log"

    def __call__(
        self, message: str, /, **kwargs: Unpack[dto.LogInput]
    ) -> dto.LogDTO:
        # LATER: prepare more stuff here instead of e.g. LogEmitter
        return self.dto_cls.create(message=message, **kwargs)


class CliDtoProducer(DtoProducer[dto.CliDTO]):
    dto_name: dto.DtoNames = "cli"

    def __call__(
        self, content: Sequence[dto.CliSpec], /, **kwargs: Unpack[dto.CliInput]
    ) -> dto.CliDTO:
        return self.dto_cls.create(tuple(content), **kwargs)


#  LINE: -- Cli Specifications -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PanelDtoProducer(DtoProducer[dto.PanelDTO]):
    dto_name: dto.DtoNames = "panel"

    def __call__(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(*content, **kwargs)


class MarkdownDtoProducer(DtoProducer[dto.MarkdownDTO]):
    dto_name: dto.DtoNames = "markdown"

    def __call__(
        self, content: Stringable, /, **kwargs: Unpack[dto.MarkdownInput]
    ) -> dto.MarkdownDTO:
        return self.dto_cls.create(content, **kwargs)


class LineDtoProducer(DtoProducer[dto.LineDTO]):
    dto_name: dto.DtoNames = "line"

    def __call__(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.LineInput]
    ) -> dto.LineDTO:
        return self.dto_cls.create(content, **kwargs)


class TableDtoProducer(DtoProducer[TableViewDTO]):
    dto_name: dto.DtoNames = "table"

    def __call__(
        self,
        content: dto._Grid,
        /,
        **kwargs: Unpack[dto.TableInput],
    ) -> TableViewDTO:
        return self.dto_cls.create(content, **kwargs)

    def matrix(
        self,
        matrix: Sequence[Sequence[dto.CliSpec]],
        /,
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_matrix(matrix, **kw)

    def rows(
        self,
        rows: Mapping[str, dto.CliSpec | Sequence[dto.CliSpec]],
        /,
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_rows(rows, **kw)

    def cols(
        self,
        cols: Mapping[str, Sequence[Any]],
        /,
        *,
        corner: str = "",
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_cols(cols, corner=corner, **kw)

    def records(
        self,
        records: Sequence[Mapping[str, Any]],
        /,
        *,
        headers: Sequence[str] | None = None,
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_records(records, headers=headers, **kw)

    def kv(
        self,
        mapping: Mapping[str, Any],
        /,
        *,
        key_col: str = "Key",
        val_col: str = "Value",
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_kv(
            mapping, key_col=key_col, val_col=val_col, **kw
        )
