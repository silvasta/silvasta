"""
Define the Event DTOs for Log and Print

                              DependencyLevel.sstcore.port.event[1]
"""

__all__: list[str] = [
    "EventDTO",
    "BaseEventDTO",
    "DtoNames",
    "DtoTable",
    "DtoRegistry",
    # main dtos
    "LogDTO",
    "LogInput",
    "CliDTO",
    "CliInfoInput",
    "CliInput",
    "CliSpec",
    # cli extensions
    "PanelDTO",
    "PanelInput",
    "BoxInput",
    "HeaderPresetInput",
    "StatusInput",
    "MarkdownDTO",
    "MarkdownInput",
    "LineDTO",
    "LineInput",
    "LinePresetInput",
    "TableDTO",
    "TableInput",
    "TablePresetInput",
    "MergedDtoInputs",
]

import dataclasses as _dc
import typing as _typing
from collections.abc import Callable as _Callable
from collections.abc import Mapping as _Mapping
from typing import Any as _Any
from typing import Unpack as _Unpack

from loguru import logger as _logger

from .._types import _RichView
from .._types import event_types as _et
from ..color import Color as _Color
from ..color import ColorArg as _ColorArg
from . import _param as _p

type DtoTable[T: BaseEventDTO] = _Mapping[str, type[T]]
type DtoRegistry[T: BaseEventDTO] = dict[str, type[T]]
type DtoNames = _typing.Literal[
    "log", "cli", "panel", "markdown", "line", "table", "ctor"
]


@_typing.dataclass_transform(kw_only_default=True)
class BaseEventDTO:
    """Establish DTO Registry and auto-transform all Member to SpecClass"""

    @property
    def registry(self) -> DtoTable:
        return self._registry

    _registry: DtoRegistry = {}  # LATER: ClsRegistry
    name: _typing.ClassVar[DtoNames]

    def __init_subclass__(cls, name: DtoNames, kw_only=True, **kwargs):
        super().__init_subclass__(**kwargs)

        if replaced := cls._registry.get(name):
            _logger.info(f"Replacing: {name=},{replaced=}")  # REMOVE:

        cls._registry[name] = cls
        cls.name = name

        _dc.dataclass(kw_only=kw_only, **kwargs)(cls)

    def __str__(self):
        return f"{type(self).__name__}[{self.name}]"


class EventDTO(BaseEventDTO, name="ctor"):
    @classmethod
    def create(cls, *args, **kwargs) -> _typing.Self:
        """Resolve ParamSpec Structure and Produce latest registered DTO"""
        target_cls: type[_typing.Self] = cls._registry.get(cls.name, cls)
        sanitized: dict[str, _Any] = target_cls._sanitize_kwargs(**kwargs)
        return target_cls(*args, **sanitized)

    @classmethod  # LATER: where to apply @castarg?
    def _sanitize_kwargs(
        cls, **kwargs: _Unpack[MergedDtoInputs]
    ) -> dict[str, _Any]:
        """Pack nested ParamSpec and resolve Annotated types"""
        return _p.sanitize_specs(
            fields={field.name for field in _dc.fields(class_or_instance=cls)},
            **kwargs,
        )


#  LINE: -- Log -- -- - -- -- - -- -- - -- -- - --


class LogDTO(EventDTO, name="log", kw_only=False):
    """Root (and only Member) of the Log Pipeline"""

    message: str
    level: str = "INFO"
    metrics: _et.Map = _dc.field(default_factory=dict)
    extra: _et.Map = _dc.field(default_factory=dict)

    def metainfo(self) -> dict[str, _Any]:  # LATER: here or in derived?
        return {**self.extra, **self.metrics}


class LogInput(_typing.TypedDict, total=False):
    level: str
    metrics: _et.Map
    extra: _et.Map


#  LINE: -- Cli -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CliDTO[Content = _Content](EventDTO, name="cli", kw_only=False):
    """Root of the Cli Pipeline"""

    content: Content
    color: _Color = _Color.AZURE  # Main Color
    infos: _et.Map = _dc.field(default_factory=dict)


class CliInfoInput(_typing.TypedDict, total=False):
    infos: _et.Map


class CliInput(CliInfoInput, total=False):
    color: _ColorArg


#  LINE: -- Definitions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_typing.runtime_checkable
class _LogSerializable[LogDTO_covariant: LogDTO = LogDTO](_typing.Protocol):
    def __log__(self) -> LogDTO_covariant:
        """Message the Event for Traceability"""


@_typing.runtime_checkable
class _CliSerializable[CliDTO_covariant: CliDTO = CliDTO](_typing.Protocol):
    def __cli__(self) -> CliDTO_covariant:
        """Snapshot the Target for Visualization"""


type CliSpec = _CliSerializable | _RichView | str

type _Content[Value: CliSpec | _et.Tuple[CliSpec]] = _et.Tuple[Value]
type _Vec = _Content[CliSpec]
type _Grid = tuple[tuple[CliSpec, ...], ...]

#  LINE: -- Panel -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PanelDTO(CliDTO[_Vec], name="panel"):
    """Store Spec to Render in Box"""

    header: _p.HeaderSpec = _dc.field(default_factory=_p.HeaderSpec)
    frame: _p.FrameSpec = _dc.field(default_factory=_p.FrameSpec)


class PanelInput(CliInput, _p.HeaderInput, _p.FrameInput, total=False):
    """Full manual Panel configuration"""


class BoxInput(CliInput, _p.HeaderInput, _p.FrameTopicInput, total=False):
    """Panel configuration when `box` style is fixed by a Box preset."""


class HeaderPresetInput(
    CliInput, _p.HeaderFrameInput, _p.FrameInput, total=False
):
    """Panel configuration when `title` is passed positionally."""


class StatusInput(
    CliInfoInput, _p.HeaderFrameInput, _p.FrameInput, total=False
):
    """Panel configuration when `title` and `color` are fixed by preset."""


#  LINE: -- Markdown --- -- - -- -- - -- -- - -- -- - -- -- - -- --


class MarkdownDTO(CliDTO[CliSpec], name="markdown"):
    """Store one Formatted Markdown SpecPoint"""

    frame: _p.FrameSpec = _dc.field(default_factory=_p.FrameSpec)
    maxlen: int = 400


class MarkdownInput(CliInput, _p.FrameInput, total=False):
    """Markdown"""

    maxlen: int


#  LINE: -- Line --- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LineDTO(CliDTO[_Vec], name="line"):
    """Store Lines for Sequential unboxed Rendering."""

    header: _p.HeaderSpec = _dc.field(default_factory=_p.HeaderSpec)
    stat: _Callable[[_Vec], str] | None = None


class LinePresetInput(CliInput, _p.HeaderFrameInput, total=False):
    """Line options when `title`/`stat` are computed by a preset."""


class LineInput(CliInput, _p.HeaderInput, total=False):
    stat: _Callable[[_Vec], str]


#  LINE: -- Table --- -- - -- -- - -- -- - -- -- - -- -- - -- --


class TableDTO(CliDTO[_Grid], name="table"):  # TODO: Input
    """
    Store Table Spec in Grid of Rows and Columns

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

    header: _p.HeaderSpec = _dc.field(default_factory=_p.HeaderSpec)
    frame: _p.FrameSpec = _dc.field(default_factory=_p.FrameSpec)


class TablePresetInput(CliInput, _p.HeaderInput, _p.FrameInput, total=False):
    """Table styling options when grid/headers are built by a factory method."""


class TableInput(TablePresetInput, total=False):
    """Full manual Table configuration."""

    col_names: _Content[str]
    row_names: _Content[str]
    corner: str


class MergedDtoInputs(
    TableInput, MarkdownInput, LineInput, LogInput, total=False
):
    """Combined spec space so @castarg discovers all Annotated casters once."""
