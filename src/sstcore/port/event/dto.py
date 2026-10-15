"""
Define the Event DTOs for Log and Print

- CliDTO: CliRenderable snapshot with __cli__ to Printer
- LogDTO: LogSerializable message with __log__ to Loguru

Rendering Protocols with Runtime check
- LogSerializable
- CliRenderable

                              DependencyLevel.sstcore.port.event[0]
"""

from pathlib import Path

__all__: list[str] = [
    "EventDTO",
    "CliDTO",
    "LogDTO",
    "DtoNames",
    "EventDtoFactory",
    # cli extensions
    "MarkdownDTO",
    "PanelDTO",
    "LineDTO",
    "TableDTO",
]

import dataclasses as _dc
import typing as _typing
from collections.abc import Mapping as _Mapping
from typing import Any as _Any

from loguru import logger as _logger

from .._types import _RichView, _Stringable
from ..color import Color as _Color

type DtoNames = _typing.Literal[
    "log",
    "cli",
    "panel",
    "markdown",
    "line",
    "table",
]


@_typing.dataclass_transform(kw_only_default=True)
class EventDTO:
    """Base class for all DTOs. Automatically makes subclasses dataclasses."""

    _registry: dict[str, type[_typing.Self]] = {}  # LATER: ClassRegister

    def __init_subclass__(cls, name: DtoNames, kw_only=True, **kwargs):
        super().__init_subclass__(**kwargs)

        if replaced := cls._registry.get(name):
            _logger.info(f"Replacing: {name=},{replaced=}")
        cls._registry[name] = cls
        cls.name: DtoNames = name  # AI: does this work?

        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)

    def __str__(self):
        return f"{type(self).__name__}[{self.name}]"  # AI: does this work?


#  LINE: -- Factory -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EventDtoFactory(_typing.Protocol):
    """Produce the Default DTOs or their extended Versions"""

    def log(self) -> LogDTO: ...
    def cli(self) -> CliDTO: ...
    def panel(self) -> PanelDTO: ...
    def markdown(self) -> MarkdownDTO: ...
    def line(self) -> LineDTO: ...
    def table(self) -> TableDTO: ...


#  LINE: -- Log -- -- - -- -- - -- -- - -- -- - --


@_typing.runtime_checkable
class _LogSerializable[LogDTO_covariant: LogDTO = LogDTO](_typing.Protocol):
    def __log__(self) -> LogDTO_covariant:
        """Message the Event for Traceability"""


class LogDTO(EventDTO, name="log"):
    """Root (and only Member) of the Log Pipeline"""

    message: str
    level: str = "INFO"
    metrics: _Map = _dc.field(default_factory=dict)
    extra: _Map = _dc.field(default_factory=dict)


#  LINE: -- Cli -- -- - -- -- - -- -- - -- -- - --


@_typing.runtime_checkable
class _CliRenderable[CliDTO_covariant: CliDTO = CliDTO](_typing.Protocol):
    def __cli__(self) -> CliDTO_covariant:
        """Snapshot the Target for Visualization"""


# IDEA: 1 - avoid _CliRenderable in type union
_CliSerializable = _Stringable | _RichView

# IDEA: 2 - use type alias
type _CliSerializing = _CliRenderable | _Stringable | _RichView

# NOTE: anyway use Stringable! render handles this and drastically increases incoming selection


type _Map[Value = _Any] = _Mapping[str, Value]  # MOVE: port._types
type _Vec[Value: _CliSerializing = _CliSerializing] = tuple[Value]


class CliDTO[
    Content = _Vec,
](
    EventDTO,
    name="cli",
    kw_only=False,
):
    """Root of the Cli Pipeline"""

    content: Content
    color: _Color = _Color.AZURE  # Main Color
    data: _Map = _dc.field(default_factory=dict)


@_dc.dataclass(kw_only=True)
class _HeaderMixin[
    Header: tuple,
]:
    """Slim optional Frame with Title on top of the Content"""

    title: str | None = None  # intended as text inside the header
    header: Header = _dc.field(default_factory=tuple)


# IDEA: make them as well EventDTO, but without Factory and Rendering
# - just track them in a hidden registry part, update them?
# ok.. might be difficult to mix that proper into the target DTO
# -> maybe easier to update the MixinParam and inject the NamedTuple


@_dc.dataclass(kw_only=True)
class _FrameMixin[
    Frame: FrameParam = FrameParam,
]:
    """The Box around the Renderable"""

    frame: Frame = _dc.field(default_factory=tuple)


class FrameParam(_typing.NamedTuple): ...


class PanelDTO[
    Content = _Vec,
    Frame: FrameParam = FrameParam,
    Header: tuple = tuple,
](
    _FrameMixin[Frame],
    _HeaderMixin[Header],
    CliDTO[Content],
    name="panel",
):
    """Store Data to Render in Box"""

    topic: str | None = None  # upper title inside frame-line


class MarkdownDTO[
    Content = _Stringable,
    Frame: FrameParam = FrameParam,
](
    _FrameMixin[Frame],
    CliDTO[Content],
    name="markdown",
):
    """Store formatted Markdown Data"""


class LineDTO[
    Content = _Vec,
    Header: tuple = tuple,
](
    CliDTO[Content],
    _HeaderMixin[Header],
    name="line",
):
    """Store Multiple or Singe Line or simple Rule"""


class TableDTO[
    Content = _Vec[_Vec],
    Frame: FrameParam = FrameParam,
    Header: tuple = tuple,
](
    CliDTO[Content],
    _FrameMixin[Frame],
    _HeaderMixin[Header],
    name="table",
):
    """
    Store Table Data as Rows containing (splitted) Columns

     - [ 0][ 0] corner
     - [ 0][1:] col_names
     - [1:][ 0] row_names
     - [1:][1:] content
    """

    col_names: _Vec[str] = _dc.field(default_factory=tuple)
    row_names: _Vec[str] = _dc.field(default_factory=tuple)
    corner: str = ""


if __name__ == "__main__":

    class HeaderSpec(_typing.NamedTuple):
        topic: str
        title_color: _Color
        topic_color: _Color

    class FrameSpec(FrameParam):
        box: str
        title_color: _Color
        topic_color: _Color

    content: list[Path] = [Path.cwd(), Path.cwd(), Path.cwd()]  # not tuple?
    test: PanelDTO[_Stringable, FrameSpec, HeaderSpec] = PanelDTO(content)

    _typing.reveal_type(test.frame.box)  # AI: code runs until here
    _typing.reveal_type(test.header.title_color)
