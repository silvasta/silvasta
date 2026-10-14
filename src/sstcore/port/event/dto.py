"""
Define the Event DTOs for Log and Print

- CliDTO: CliRenderable snapshot with __cli__ to Printer
- LogDTO: LogSerializable message with __log__ to Loguru

Rendering Protocols with Runtime check
- LogSerializable
- CliRenderable

                              DependencyLevel.sstcore.port.event[0]
"""

__all__: list[str] = [
    "EventDTO",
    "LogDTO",
    "CliDTO",
    "EventDtoFactory",
    "DtoNames",
    # cli extensions
    "MarkdownDTO",
    "PanelDTO",
    "LineDTO",
    "GroupDTO",  # CHECK:
    "TableDTO",
]

import dataclasses as _dc
import typing as _typing  # LATER: import _Any directly?
from collections.abc import Iterable as _Iterable

from loguru import logger as _logger

from .._types import _Richable
from ..color import Color as _Color
from ..color import ColorId as _ColorId

type DtoNames = _typing.Literal[
    "log",
    "cli",
    "panel",
    "markdown",
    "group",  # CHECK:
    "line",
    "table",
]


@_typing.dataclass_transform(kw_only_default=True)
class EventDTO:
    """Base class for all DTOs. Automatically makes subclasses dataclasses."""

    _registry: dict[str, type[_typing.Self]] = {}

    def __init_subclass__(cls, name: DtoNames, kw_only=True, **kwargs):
        super().__init_subclass__(**kwargs)

        if replaced := cls._registry.get(name):  # TODO: (port-)emit?
            _logger.info(f"Replacing: {name=},{replaced=}")
        cls._registry[name] = cls

        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)


#  LINE: -- Factory -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EventDtoFactory(_typing.Protocol):
    """Produce the Default DTOs or their extended Versions"""

    def log(self) -> LogDTO: ...
    def cli(self) -> CliDTO: ...
    def panel(self) -> PanelDTO: ...
    def markdown(self) -> MarkdownDTO: ...
    def group(self) -> GroupDTO: ...  # CHECK:
    def line(self) -> LineDTO: ...
    def table(self) -> TableDTO: ...


#  LINE: -- Main branches -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDTO(EventDTO, name="log"):
    """Root (and only Member) of the Log Pipeline"""

    message: str
    level: str = "INFO"
    metrics: dict[str, _typing.Any] = _dc.field(default_factory=dict)
    extra: dict[str, _typing.Any] = _dc.field(default_factory=dict)


class CliDTO(EventDTO, name="cli", kw_only=False):
    """Root of the Cli Pipeline"""

    # NEXT: check what content actually needs
    # - rich preferably just as extension
    # - maybe resolve GroupDTO with that
    #   -> handled in renderer to rich.Group (or any other adapter)
    content: _CliRenderable | _Iterable[_CliRenderable]
    color: _ColorId = _Color.AZURE
    indent: int = 0
    meta: dict[str, _typing.Any] = _dc.field(default_factory=dict)


#  LINE: -- Views (exposed in port.represent) -- -- - -- -- - -- -- - -- -- - --


@_typing.runtime_checkable
class _CliSerializable[CliDTO_covariant: CliDTO = CliDTO](_typing.Protocol):
    def __cli__(self) -> CliDTO_covariant:
        """Snapshot the Target for Visualization"""


@_typing.runtime_checkable
class _LogSerializable(_typing.Protocol):
    def __log__(self) -> LogDTO:
        """Message the Event for Traceability"""


_CliRenderable = _CliSerializable | _Richable  # NOTE: | str included _Richable


#  LINE: -- CliDTO extensions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


_AlignMethod = _typing.Literal["left", "center", "right"]


class PanelDTO(CliDTO, name="panel"):
    # NEXT: compare with printer TypedDict kwargs,
    # -> remove as much as possible here
    # only the actual panel info, maybe some rendering hints
    frame: _Color = _Color.AZURE
    text_color: _Color = _Color.WHITE
    title: str | None = None
    # TASK: filter out the to much render information
    title_align: _AlignMethod = "right"
    expand: bool = True
    padding: tuple = (0, 1)
    metrics: dict[str, _typing.Any] = _dc.field(default_factory=dict)


class MarkdownDTO(CliDTO, name="markdown"):
    header: int = 0


class LineDTO(CliDTO, name="line"): ...


class GroupDTO(CliDTO, name="group"):
    # INFO: never used in sstcore, used in sachmis:
    # def __cli__(self) -> CliDTO:
    #     return GroupDTO(
    #         items=[
    #             PanelDTO(text=str(self), title=self.arbo_location()),
    #             MarkdownDTO(text=self.content), ] ,)
    # INFO: sachmis usage 2/2:
    # def __cli__(self) -> CliDTO:
    #     return GroupDTO(
    #         items=[
    #             PanelDTO(text=str(self), title=self.arbo_location()),
    #             MarkdownDTO(text=self.content),
    #             TableDTO.from_col_dicts(cols=self.usage), ],)
    """Stack multiple renderable Views"""


class TableDTO(CliDTO, name="table"):
    """
    Store Table Data as List of Rows containing Lists of Values

     - [1:][1:] Main content
     - [ 0][1:] Header: col_names
     - [1:][ 0] Sidebar: row_names
     - [ 0][ 0] Top-left element

    """

    matrix: list[list[_typing.Any]]
    col_names: list[str] = _dc.field(default_factory=list)
    row_names: list[str] = _dc.field(default_factory=list)
    corner: str = ""
