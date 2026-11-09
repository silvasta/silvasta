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
from typing import Any, Protocol
from typing import Unpack as _U  # noqa: N814

from .._types import EventTypes as _ET  # noqa: N814
from .._types import _Stringable
from . import _param as _p
from .dto import CliDTO, LineDTO, LogDTO, MarkdownDTO, PanelDTO, TableDTO


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
        self, message: str, /, **kwargs: _U[_p.LogInput]
    ) -> LogDTO: ...


class CliDelivering(Protocol):
    def __call__(
        self, content: _ET.Content, /, **kwargs: _U[_p.CliInput]
    ) -> CliDTO: ...


class PanelDelivering(Protocol):
    def __call__(
        self, *content: _ET.CliSpec, **kwargs: _U[_p.PanelInput]
    ) -> PanelDTO: ...


class MarkdownDelivering(Protocol):
    def __call__(
        self, content: _Stringable, /, **kwargs: _U[_p.MarkdownInput]
    ) -> MarkdownDTO: ...


class LineDelivering(Protocol):
    def __call__(
        self, *content: _ET.CliSpec, **kwargs: _U[_p.LineInput]
    ) -> LineDTO: ...


class TableDelivering(Protocol):
    def __call__(
        self, content: _ET.Grid, /, **kwargs: _U[_p.TableInput]
    ) -> TableDTO: ...

    def matrix(
        self,
        matrix: Sequence[Sequence[_ET.CliSpec]],
        /,
        **kwargs: _U[_p.TablePresetInput],
    ) -> TableDTO: ...

    def rows(
        self,
        rows: Mapping[str, _ET.CliSpec | Sequence[_ET.CliSpec]],
        /,
        **kwargs: _U[_p.TablePresetInput],
    ) -> TableDTO: ...

    def cols(
        self,
        cols: Mapping[str, Sequence[Any]],
        /,
        *,
        corner: str = "",
        **kwargs: _U[_p.TablePresetInput],
    ) -> TableDTO: ...

    def records(
        self,
        records: Sequence[Mapping[str, Any]],
        /,
        *,
        headers: Sequence[str] | None = None,
        **kwargs: _U[_p.TablePresetInput],
    ) -> TableDTO: ...

    def kv(
        self,
        mapping: Mapping[str, Any],
        /,
        *,
        key_col: str = "Key",
        val_col: str = "Value",
        **kwargs: _U[_p.TablePresetInput],
    ) -> TableDTO: ...
