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
import enum as _e
import typing as _typing
from collections.abc import Callable as _Callable
from typing import Any as _Any
from typing import Unpack as _Unpack

from loguru import logger as _logger

from .._types import _RichView, _Stringable
from .._types import event_types as _dto
from ..color import Color as _Color
from ..color import ColorArg as _ColorArg
from ..solid import BoxOption as _BoxOption


@_typing.dataclass_transform(kw_only_default=True)
class EventDTO:
    """Base class for all DTOs. Automatically makes subclasses dataclasses."""

    _registry: dict[str, type[_typing.Self]] = {}  # LATER: ClsRegistry
    name: _typing.ClassVar[DtoNames]  # AI: does this work?

    def __init_subclass__(cls, name: DtoNames, kw_only=True, **kwargs):
        super().__init_subclass__(**kwargs)

        if replaced := cls._registry.get(name):
            _logger.info(f"Replacing: {name=},{replaced=}")

        cls._registry[name] = cls
        cls.name: DtoNames = name  # AI: does this work?

        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)

    def __str__(self):
        return f"{type(self).__name__}[{self.name}]"

    @classmethod
    def create(cls): ...  # AI_QUESTION: useful over multiple derivatives?


type DtoNames = _typing.Literal[
    "log",
    "cli",
    "panel",
    "markdown",
    "line",
    "table",
]

type _CliData = _CliSerializable | _RichView | str
type _Content[Value: _CliData | _dto.Tuple[_CliData]] = _dto.Tuple[Value]
type _Vec = _Content[_CliData]
type _Grid = _Content[_dto.Tuple[_CliData]]


@_typing.runtime_checkable
class _LogSerializable[LogDTO_covariant: LogDTO = LogDTO](_typing.Protocol):
    def __log__(self) -> LogDTO_covariant:
        """Message the Event for Traceability"""


@_typing.runtime_checkable
class _CliSerializable[CliDTO_covariant: CliDTO = CliDTO](_typing.Protocol):
    def __cli__(self) -> CliDTO_covariant:
        """Snapshot the Target for Visualization"""


#  LINE: -- Factory -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EventDtoFactory(_typing.Protocol):
    """Produce the Default DTOs or their extended Versions"""

    def log(self, message: str, /, **kw: _Unpack[LogSpec]) -> LogDTO: ...
    def cli(self, content: _Content, /, **kw: _Unpack[CliSpec]) -> CliDTO: ...
    def panel(
        self, *content: _CliData, **kw: _Unpack[PanelSpec]
    ) -> PanelDTO: ...
    def markdown(
        self, content: _Stringable, /, **kw: _Unpack[MdSpec]
    ) -> MarkdownDTO: ...
    def line(self, *content: _CliData, **kw: _Unpack[LineSpec]) -> LineDTO: ...
    def table(
        self, content: _Grid, /, **kw: _Unpack[TableSpec]
    ) -> TableDTO: ...


#  LINE: -- Log -- -- - -- -- - -- -- - -- -- - --


class LogDTO(EventDTO, name="log"):
    """Root (and only Member) of the Log Pipeline"""

    message: str
    level: str = "INFO"
    metrics: _dto.Map = _dc.field(default_factory=dict)
    extra: _dto.Map = _dc.field(default_factory=dict)


class LogSpec(_typing.TypedDict):
    level: str
    metrics: _dto.Map
    extra: _dto.Map


#  LINE: -- Cli -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CliDTO[
    Content = _Content,
](EventDTO, name="cli", kw_only=False):
    """Root of the Cli Pipeline"""

    content: Content
    color: _Color = _Color.AZURE  # Main Color
    infos: _dto.Map = _dc.field(default_factory=dict)


class CliSpec(_typing.TypedDict):
    # AI: is Annotaded fine on TypedDict?
    # INFO: type _ColorArg = Annotated[ColorId, Color.resolve]
    color: _ColorArg
    infos: _dto.Map


#  LINE: -- Param -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Boxes(_BoxOption):
    CORNER = _e.auto()
    ROUND = _e.auto()
    UP = _e.auto()
    DOWN = _e.auto()
    MINI = _e.auto()
    MINI_UP = _e.auto()
    MINI_DOWN = _e.auto()
    OPEN = _e.auto()


@_typing.dataclass_transform(kw_only_default=True)
class ParamData:
    """Base for stacked configuration dataclasses (FrameData, HeaderData, etc.)."""

    def __init_subclass__(cls, kw_only: bool = True, **kwargs: _Any):
        super().__init_subclass__(**kwargs)
        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)


def _param_field[T](factory: _Callable[[], _Any], /) -> T:
    """Helper to provide a default base ParamData factory for a generic field T."""
    return _dc.field(default_factory=factory)


class FrameData(ParamData):
    """The Box around the Renderable - supplies Content and Frame"""

    topic: str | None = ""
    topic_color: _Color = _Color.WHITE
    box: Boxes = Boxes.CORNER


class FrameSpec(_typing.TypedDict, total=False):
    """Define the Border of one Header or Main Content"""

    topic: str
    topic_color: _ColorArg
    box: Boxes


class HeaderData[
    F: FrameData = FrameData,
](ParamData):
    """
    Explain:

    X --- --- --- --- --- --- --- --- --- --- [ topic: FileScan ] --- X
    | title: Frame with Title on top of the Content                   |
    X --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- X
    | content: ...                 (maybe double line for transition) |
    |          ...                                                    |

    - No Header for title = None
    - Mirror main frame topic for frame.topic = "", empty for None
    """

    title: str | None = None
    frame: F = _param_field(FrameData)


class HeaderBaseSpec(_typing.TypedDict, total=False):
    title: str


class HeaderFrameSpec(_typing.TypedDict, total=False):
    """Test"""

    header_topic: str
    header_topic_color: _ColorArg
    header_box: Boxes | None  # None = Same as Main Content


class HeaderSpec(HeaderBaseSpec, HeaderFrameSpec):
    """Combine Header with Frame Args"""


#  LINE: -- Panel -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# AI_FOCUS: Example starts here
class PanelDTO[
    H: HeaderData[_Any] = HeaderData[FrameData],
    F: FrameData = FrameData,
](CliDTO[_Vec], name="panel"):
    """Store Data to Render in Box"""

    header: H = _param_field(HeaderData)
    frame: F = _param_field(FrameData)


# AI: Idea 1
class _PanelDTO[H: HeaderData, F: FrameData](CliDTO[_Vec], name="panel"):
    """Store Data to Render in Box"""

    header: HeaderData[F]
    frame: F


# AI: Idea 2
class _PanelDTO(CliDTO[_Vec], name="panel"):
    """Store Data to Render in Box"""

    header: HeaderData
    frame: FrameData


class PanelSpec(HeaderSpec, FrameSpec):
    """Box-Like"""


#  LINE: -- Markdown --- -- - -- -- - -- -- - -- -- - -- -- - -- --


class MarkdownDTO[
    F: FrameData = FrameData,
](CliDTO[tuple[_CliData]], name="markdown"):
    """Store one Formatted Markdown DataPoint"""

    frame: F = _param_field(FrameData)
    maxlen: int = 400


class MdSpec(FrameSpec):
    """Markdown"""

    maxlen: int


#  LINE: -- Line --- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LineDTO[
    H: HeaderData = HeaderData,
](CliDTO[_Vec], name="line"):
    """Store Lines for Sequential unboxed Rendering"""

    header: H = _param_field(HeaderData)
    stat: _Callable[[_Vec], str] | None = lambda lines: (
        f"Total Lines: {len(lines)}"
    )


class LineSpec(HeaderSpec):
    """Line and Lines"""

    maxlen: int
    stat: _Callable[[_Vec], str]


#  LINE: -- Table --- -- - -- -- - -- -- - -- -- - -- -- - -- --


class TableDTO[
    H: HeaderData[_Any] = HeaderData[FrameData],
    F: FrameData = FrameData,
](CliDTO[_Grid], name="table"):
    """
    Store Table Data in Grid of Rows and Columns

     - [ 0][ 0] corner
     - [ 0][1:] col_names
     - [1:][ 0] row_names
     - [1:][1:] content

     corner  | col_name | col_name | col_name |
    --- --- -X- --- --- --- --- --- --- --- ---
    row_name | content  | content  | content  |
    row_name | content  | content  | content  |
    """

    col_names: _Content[str] = _dc.field(default_factory=tuple)
    row_names: _Content[str] = _dc.field(default_factory=tuple)
    corner: str = ""

    header: H = _param_field(HeaderData)
    frame: F = _param_field(FrameData)


class TableSpec(HeaderSpec, FrameSpec):
    """Line and Lines"""

    col_names: _Content[str]
    row_names: _Content[str]
    corner: str
