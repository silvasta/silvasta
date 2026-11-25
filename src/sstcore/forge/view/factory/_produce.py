"""
Prepare Functors, 1 per DTO

- add optional safe mode
- handle stacked functions

              DependencyLevel.sstcore.forge.view.factory[c.2.4.0.1]
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

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, Self
from typing import Unpack as _U  # noqa:N814

from ....brick.color import colorize
from ....port import functorial
from ....port._types import EventTypes as _ET  # noqa:N814
from ....port.event import _param as _p
from ....port.event import dto
from ....port.link import portlink
from ....port.represent import (
    CliSerializable,
    LogSerializable,
    PydanticModel,
    RichConsolable,
    RichView,
)
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

    @classmethod
    def to_spec(cls, target: object, /) -> _ET.CliSpec:
        """Coerce any single Python object into a strict DTO-ready CliSpec."""
        match target:
            case CliSerializable():
                return target
            case RichView() | RichConsolable() | str() | PydanticModel():
                return target  # ty: ignore
            case LogSerializable():
                return target.__log__().message
            case Path() as path:
                return colorize.path(path)
            case type():
                return colorize.modules(target)
            case Iterable() as items if not isinstance(
                target, (bytes, Mapping)
            ):
                return "\n".join(str(cls.to_spec(i)) for i in items)
            case _:
                return str(target)

    @classmethod
    def to_vec(cls, *content: object) -> _ET.Vec:
        """Flatten optional single sequence and normalize all items to a tuple of CliSpec."""
        if (
            len(content) == 1
            and isinstance(content[0], Iterable)
            and not isinstance(
                content[0], (str, bytes, Mapping, PydanticModel, RichView)
            )
        ):
            return tuple(cls.to_spec(item) for item in content[0])
        return tuple(cls.to_spec(item) for item in content)

    @classmethod
    def to_grid(cls, grid: Sequence[Sequence[object]], /) -> _ET.Grid:
        """Normalize a 2D sequence of arbitrary objects into a strict DTO Grid."""
        return tuple(tuple(cls.to_spec(cell) for cell in row) for row in grid)


#  LINE: -- Log and Cli Base -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDtoProducer(DtoProducer[dto.LogDTO]):
    dto_name: dto.DtoNames = "log"

    def __call__(
        self, message: object, /, **kwargs: _U[_p.LogInput]
    ) -> dto.LogDTO:
        return self.dto_cls.create(message=str(self.to_spec(message)), **kwargs)


class CliDtoProducer(DtoProducer[dto.CliDTO]):
    dto_name: dto.DtoNames = "cli"

    def __call__(
        self, *content: _ET.CliItem, **kwargs: _U[_p.CliInput]
    ) -> dto.CliDTO:
        return self.dto_cls.create(self.to_vec(*content), **kwargs)


#  LINE: -- Cli Specifications -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PanelDtoProducer(DtoProducer[dto.PanelDTO]):
    dto_name: dto.DtoNames = "panel"

    def __call__(
        self, *content: _ET.CliItem, **kwargs: _U[_p.PanelInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(self.to_vec(*content), **kwargs)


class MarkdownDtoProducer(DtoProducer[dto.MarkdownDTO]):
    dto_name: dto.DtoNames = "markdown"

    def __call__(
        self, content: _ET.CliItem, /, **kwargs: _U[_p.MarkdownInput]
    ) -> dto.MarkdownDTO:
        return self.dto_cls.create(str(self.to_spec(content)), **kwargs)


class LineDtoProducer(DtoProducer[dto.LineDTO]):
    dto_name: dto.DtoNames = "line"

    def __call__(
        self, *content: _ET.CliItem, **kwargs: _U[_p.LineInput]
    ) -> dto.LineDTO:
        return self.dto_cls.create(self.to_vec(*content), **kwargs)

    def len(
        self,
        name: str,
        *content: _ET.CliItem,
        **kw: _U[_p.LinePresetInput],
    ) -> dto.LineDTO:
        items: _ET.Vec = self.to_vec(*content)
        header_title = f"{name}: {len(items)}"
        merged: dict[str, Any] = dict(kw)
        merged.setdefault("header_topic", name)
        return self(
            *items,
            title=header_title,
            stat=lambda vec: f"{name}: {len(vec)}",
            **merged,
        )


class TableDtoProducer(DtoProducer[TableViewDTO]):
    dto_name: dto.DtoNames = "table"

    def __call__(
        self, content: _ET.MatrixInput, /, **kwargs: _U[_p.TableInput]
    ) -> TableViewDTO:
        return self.dto_cls.create(self.to_grid(content), **kwargs)

    def matrix(
        self,
        matrix: _ET.MatrixInput,
        /,
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_matrix(self.to_grid(matrix), **kw)

    def rows(
        self,
        rows: _ET.RowsInput,
        /,
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        normalized_rows: dict[str, _ET.CliSpec | Sequence[_ET.CliSpec]] = {
            k: (
                self.to_vec(v)
                if isinstance(v, Sequence) and not isinstance(v, (str, bytes))
                else self.to_spec(v)
            )
            for k, v in rows.items()
        }
        return self.dto_cls.from_rows(normalized_rows, **kw)

    def cols(
        self,
        cols: _ET.ColsInput,
        /,
        *,
        corner: str = "",
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_cols(cols, corner=corner, **kw)

    def records(
        self,
        records: _ET.RecordsInput,
        /,
        *,
        headers: Sequence[str] | None = None,
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_records(records, headers=headers, **kw)

    def kv(
        self,
        mapping: _ET.KvInput,
        /,
        *,
        key_col: str = "Key",
        val_col: str = "Value",
        **kw: _U[_p.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_kv(
            mapping, key_col=key_col, val_col=val_col, **kw
        )
