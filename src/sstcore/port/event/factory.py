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
    "BoxDelivering",
    "HeaderDelivering",
    "StatusDelivering",
    "MarkdownDelivering",
    "LineDelivering",
    "TableDelivering",
]


from collections.abc import Mapping, Sequence
from typing import Any, Literal, Protocol, Unpack

from .._types import _Stringable
from ..color import ColorArg
from . import dto
from ._param import _Boxes


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


class BoxDelivering(Protocol):
    def __call__(
        self,
        *content: dto.CliSpec,
        box: _Boxes = _Boxes.OPEN,
        **kw: Unpack[dto.BoxInput],
    ) -> dto.PanelDTO: ...

    def open(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def round(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def corner(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def up(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def down(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def mini(
        self,
        *content: dto.CliSpec,
        mode: Literal["up", "down", "both"] = "both",
        **kw: Unpack[dto.BoxInput],
    ) -> dto.PanelDTO: ...
    def mini_up(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...
    def mini_down(
        self, *content: dto.CliSpec, **kw: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO: ...


class HeaderDelivering(Protocol):
    def __call__(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.HeaderPresetInput],
    ) -> dto.PanelDTO: ...

    def dip(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        color: ColorArg = ...,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO: ...

    def invert(
        self,
        title: str,
        *content: dto.CliSpec,
        color: ColorArg = ...,
        invert_color: ColorArg = ...,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO: ...


class StatusDelivering(Protocol):
    def __call__(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO: ...


class MarkdownDelivering(Protocol):
    def __call__(
        self, content: _Stringable, /, **kw: Unpack[dto.MarkdownInput]
    ) -> dto.MarkdownDTO: ...


class LineDelivering(Protocol):
    def __call__(
        self, *content: dto.CliSpec, **kw: Unpack[dto.LineInput]
    ) -> dto.LineDTO: ...

    def len(
        self,
        name: str,
        *content: dto.CliSpec | Sequence[dto.CliSpec],
        **kw: Unpack[dto.LinePresetInput],
    ) -> dto.LineDTO: ...


class TableDelivering(Protocol):
    def __call__(
        self, content: dto._Grid, /, **kw: Unpack[dto.TableInput]
    ) -> dto.TableDTO: ...

    def matrix(
        self,
        matrix: Sequence[Sequence[dto.CliSpec]],
        /,
        **kw: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...

    def rows(
        self,
        rows: Mapping[str, dto.CliSpec | Sequence[dto.CliSpec]],
        /,
        **kw: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...

    def cols(
        self,
        cols: Mapping[str, Sequence[Any]],
        /,
        *,
        corner: str = "",
        **kw: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...

    def records(
        self,
        records: Sequence[Mapping[str, Any]],
        /,
        *,
        headers: Sequence[str] | None = None,
        **kw: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...

    def kv(
        self,
        mapping: Mapping[str, Any],
        /,
        *,
        key_col: str = "Key",
        val_col: str = "Value",
        **kw: Unpack[dto.TablePresetInput],
    ) -> dto.TableDTO: ...
