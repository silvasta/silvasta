"""
Define the Shape of the DTO Factory

                              DependencyLevel.sstcore.port.event[2]
"""

__all__: list[str] = [
    "EventDtoFactory",
    #
    "LogDelivering",
    "CliDelivering",
    "PanelDelivering",
    "MarkdownDelivering",
    "LineDelivering",
    "TableDelivering",
]


# TODO: external imports _privat
from collections.abc import Mapping, Sequence
from typing import Any, Protocol, Unpack

from .._types import _Stringable
from . import dto


class EventDtoFactory(Protocol):
    """Define the Producers that Deliver the DTOs"""

    @property
    def log(self) -> LogDelivering: ...
    @property
    def cli(self) -> CliDelivering: ...
    @property
    def panel(self) -> PanelDelivering: ...
    @property
    def md(self) -> MarkdownDelivering: ...
    @property
    def line(self) -> LineDelivering: ...
    @property
    def table(self) -> TableDelivering: ...


class LogDelivering(Protocol):
    def __call__(
        self, message: str, /, **kwargs: Unpack[dto.LogInput]
    ) -> dto.LogDTO: ...


class CliDelivering(Protocol):
    def __call__(
        self, content: dto._Content, /, **kwargs: Unpack[dto.CliInput]
    ) -> dto.CliDTO: ...


class PanelDelivering(Protocol):
    def __call__(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO: ...


class MarkdownDelivering(Protocol):
    def __call__(
        self, content: _Stringable, /, **kwargs: Unpack[dto.MarkdownInput]
    ) -> dto.MarkdownDTO: ...


class LineDelivering(Protocol):
    def __call__(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.LineInput]
    ) -> dto.LineDTO: ...


class TableDelivering(Protocol):
    def __call__(
        self, content: dto._Grid, /, **kwargs: Unpack[dto.TableInput]
    ) -> dto.TableDTO: ...

    def matrix(
        self,
        matrix: Sequence[Sequence[dto.CliSpec]],
        /,
        **kwargs: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...

    def rows(
        self,
        rows: Mapping[str, dto.CliSpec | Sequence[dto.CliSpec]],
        /,
        **kwargs: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...

    def cols(
        self,
        cols: Mapping[str, Sequence[Any]],
        /,
        *,
        corner: str = "",
        **kwargs: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...

    def records(
        self,
        records: Sequence[Mapping[str, Any]],
        /,
        *,
        headers: Sequence[str] | None = None,
        **kwargs: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...

    def kv(
        self,
        mapping: Mapping[str, Any],
        /,
        *,
        key_col: str = "Key",
        val_col: str = "Value",
        **kwargs: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...
