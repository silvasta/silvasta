import typing as _typing
from collections.abc import Sequence
from typing import Any, Protocol, Unpack
from typing import Unpack as _Unpack

from .._types import _Stringable
from .dto import (
    CliData,
    CliDTO,
    CliSpec,
    LineDTO,
    LineSpec,
    LogDTO,
    LogSpec,
    MarkdownDTO,
    MarkdownSpec,
    PanelDTO,
    PanelSpec,
    TableDTO,
    TableSpec,
    _Content,
    _Grid,
)


class LogDelivering(Protocol):
    def __call__(self, message: str, /, **kw: Unpack[LogSpec]) -> LogDTO: ...


class CliDelivering(Protocol):
    def __call__(
        self, content: _Content, /, **kw: Unpack[CliSpec]
    ) -> CliDTO: ...


class TableDelivering(Protocol):
    def __call__(
        self, content: _Grid, /, **kw: Unpack[TableSpec]
    ) -> TableDTO: ...
    def from_cols(
        self, cols: dict[str, Sequence[Any]], *, corner: str = ""
    ) -> TableDTO: ...


class EventDtoFactory3(Protocol):
    # AI: most likely the selected approach
    # - the Printer and Emitter will be the public facades,
    # -> I will finish the protocols here together with that
    @property
    def log(self) -> LogDelivering: ...
    @property
    def cli(self) -> CliDelivering: ...
    # @property
    # def panel(self) -> PanelDelivering: ...
    # @property
    # def md(self) -> MarkdownDelivering: ...
    # @property
    # def line(self) -> LineDelivering: ...
    @property
    def table(self) -> TableDelivering: ...


class EventDtoFactory2(Protocol):
    # REMOVE: works but with @property is more precise
    log: LogDelivering
    cli: CliDelivering
    # panel: PanelDelivering
    # md: MarkdownDelivering
    # line: LineDelivering
    table: TableDelivering


class EventDtoFactory1(_typing.Protocol):
    # REMOVE: undesired for functors with additional methods
    """Produce the Default DTOs or their extended Versions"""

    def log(self, message: str, /, **kw: _Unpack[LogSpec]) -> LogDTO: ...
    def cli(self, content: _Content, /, **kw: _Unpack[CliSpec]) -> CliDTO: ...
    def panel(
        self, *content: CliData, **kw: _Unpack[PanelSpec]
    ) -> PanelDTO: ...
    def md(
        self, content: _Stringable, /, **kw: _Unpack[MarkdownSpec]
    ) -> MarkdownDTO: ...
    def line(self, *content: CliData, **kw: _Unpack[LineSpec]) -> LineDTO: ...
    def table(
        self, content: _Grid, /, **kw: _Unpack[TableSpec]
    ) -> TableDTO: ...
