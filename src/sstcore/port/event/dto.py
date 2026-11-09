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
    # dtos
    "LogDTO",
    "CliDTO",
    "PanelDTO",
    "MarkdownDTO",
    "LineDTO",
    "TableDTO",
]

import dataclasses as _dc
import typing as _typing
from collections.abc import Callable as _Callable
from collections.abc import Mapping, MutableMapping
from typing import Unpack as _Unpack

from loguru import logger as _logger

from .._types import EventTypes as _ET  # noqa: N814
from ..color import Color as _Color
from ..structures import FieldSet as _FieldSet
from . import _param as _p

type DtoTable[DTO = BaseEventDTO] = Mapping[DtoNames, type[DTO]]
type DtoRegistry = MutableMapping[DtoNames, type[BaseEventDTO]]

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


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EventDTO(BaseEventDTO, name="ctor"):
    @classmethod
    def create(cls, *args, **kwargs) -> _typing.Self:
        """Resolve ParamSpec Structure and Produce latest registered DTO"""
        target_cls: type[_typing.Self] = cls._registry.get(cls.name, cls)  # ty:ignore
        sanitized: _ET.StrDict = target_cls._sanitize_kwargs(**kwargs)
        return target_cls(*args, **sanitized)

    @classmethod  # LATER: where to apply @castarg?
    def _sanitize_kwargs(
        cls, **kwargs: _Unpack[_p.MergedDtoInputs]
    ) -> _ET.StrDict:
        """Pack nested ParamSpec and resolve Annotated types"""
        return _p.sanitize_kwargs(fields=_FieldSet.absorb(cls), **kwargs)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDTO(EventDTO, name="log", kw_only=False):
    """Root (and only Member) of the Log Pipeline"""

    message: str
    level: str = "INFO"
    metrics: _ET.Map = _dc.field(default_factory=dict)
    extra: _ET.Map = _dc.field(default_factory=dict)

    def metainfo(self) -> _ET.StrDict:  # LATER: here or in derived?
        return {**self.extra, **self.metrics}


class CliDTO[Content = _ET.Content](EventDTO, name="cli", kw_only=False):
    """Root of the Cli Pipeline"""

    content: Content
    color: _Color = _Color.AZURE  # Main Color
    infos: _ET.Map = _dc.field(default_factory=dict)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PanelDTO(CliDTO[_ET.Vec], name="panel"):
    """Store Spec to Render in Box"""

    header: _p.HeaderSpec = _dc.field(default_factory=_p.HeaderSpec)
    frame: _p.FrameSpec = _dc.field(default_factory=_p.FrameSpec)


class MarkdownDTO(CliDTO[_ET.CliSpec], name="markdown"):
    """Store one Formatted Markdown SpecPoint"""

    frame: _p.FrameSpec = _dc.field(default_factory=_p.FrameSpec)
    maxlen: int = 400


class LineDTO(CliDTO[_ET.Vec], name="line"):
    """Store Lines for Sequential unboxed Rendering."""

    header: _p.HeaderSpec = _dc.field(default_factory=_p.HeaderSpec)
    stat: _Callable[[_ET.Vec], str] | None = None


class TableDTO(CliDTO[_ET.Grid], name="table"):  # TODO: Input
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

    col_names: _ET.Content[str] = _dc.field(default_factory=tuple)
    row_names: _ET.Content[str] = _dc.field(default_factory=tuple)
    corner: str = ""

    header: _p.HeaderSpec = _dc.field(default_factory=_p.HeaderSpec)
    frame: _p.FrameSpec = _dc.field(default_factory=_p.FrameSpec)
