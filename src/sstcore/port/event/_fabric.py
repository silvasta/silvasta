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


from collections.abc import Sequence
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
        self, message: str, /, **kw: Unpack[dto.LogInput]
    ) -> dto.LogDTO: ...


class CliDelivering(Protocol):
    def __call__(
        self, content: dto._Content, /, **kw: Unpack[dto.CliInput]
    ) -> dto.CliDTO: ...


class PanelDelivering(Protocol):
    def __call__(
        self, *content: dto.CliSpec, **kw: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO: ...


class MarkdownDelivering(Protocol):
    def __call__(
        self, content: _Stringable, /, **kw: Unpack[dto.MarkdownInput]
    ) -> dto.MarkdownDTO: ...


class LineDelivering(Protocol):
    def __call__(
        self, *content: dto.CliSpec, **kw: Unpack[dto.LineInput]
    ) -> dto.LineDTO: ...


class TableDelivering(Protocol):
    def __call__(
        self, content: dto._Grid, /, **kw: Unpack[dto.TableInput]
    ) -> dto.TableDTO: ...

    # TODO: remaining methods (from forge.view.factory._table)
    def from_cols(
        self, cols: dict[str, Sequence[Any]], *, corner: str = ""
    ) -> dto.TableDTO: ...
