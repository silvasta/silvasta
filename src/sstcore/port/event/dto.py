"""
Define the Event DTOs for Log and Print

- LogDTO  Intended for __log__ and processed by Loguru.logger
- CliDTO: Intended for __cli__ and processed by printer

Rendering Protocols with Runtime check
- LogSerializable
- CliRenderable

                              DependencyLevel.sstcore.port.event[0]
"""

__all__: list[str] = [
    "CliDtoCreator",
    "LogDTO",
    "CliDTO",
    "GroupDTO",
    "LineDTO",
    "MarkdownDTO",
    "PanelDTO",
    "TableDTO",
]

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import Any as _Any
from typing import Literal as _Literal
from typing import Protocol as _Protocol
from typing import Self as _Self
from typing import dataclass_transform as _dataclass_transform
from typing import runtime_checkable as _runtime_checkable

from loguru import logger as _logger

from ..color import Color as _Color
from ..color import ColorId as _ColorId

type DtoNames = _Literal[
    "log",
    "cli",
    "panel",
    "markdown",
    "group",
    "line",
    "table",
]


@_dataclass_transform(kw_only_default=True)
class EventDTO:
    """Base class for all DTOs. Automatically makes subclasses dataclasses."""

    _registry: dict[str, type[_Self]] = {}

    def __init_subclass__(cls, name: DtoNames, kw_only=True, **kwargs):
        super().__init_subclass__(**kwargs)

        if replaced := cls._registry.get(name):  # TODO: (port-)emit?
            _logger.info(f"Replacing: {name=},{replaced=}")
        cls._registry[name] = cls

        _dataclass(kw_only=kw_only, **kwargs)(cls)


class LogDTO(EventDTO, name="log"):
    """Root (and only Member) of the Log Pipeline"""

    message: str
    level: str = "INFO"
    metrics: dict[str, _Any] = _field(default_factory=dict)
    extra: dict[str, _Any] = _field(default_factory=dict)


class CliDTO(EventDTO, name="cli", kw_only=False):
    """Root of the Cli Pipeline"""

    content: str
    color: _ColorId = _Color.AZURE
    indent: int = 0
    meta: dict[str, _Any] = _field(default_factory=dict)


_AlignMethod = _Literal["left", "center", "right"]


class PanelDTO(CliDTO, name="panel"):
    # TODO: assemble stack with color+attribute
    color: str = "bold white"
    frame: str = _Color(value=2).name
    title: str | None = None
    # TASK: filter out the to much render information
    title_align: _AlignMethod = "right"
    expand: bool = True
    padding: tuple = (0, 1)
    metrics: dict[str, _Any] = _field(default_factory=dict)


class MarkdownDTO(CliDTO, name="markdown"):
    header: int = 0


class LineDTO(CliDTO, name="line"): ...


class GroupDTO(CliDTO, name="group"):
    """Stack multiple renderable Views"""


class TableDTO(CliDTO, name="table"):
    """
    Store Table Data as List of Rows containing Lists of Values

     - [1:][1:] Main content
     - [ 0][1:] Header: col_names
     - [1:][ 0] Sidebar: row_names
     - [ 0][ 0] Top-left element

    """

    matrix: list[list[_Any]]
    col_names: list[str] = _field(default_factory=list)
    row_names: list[str] = _field(default_factory=list)
    corner: str = ""


@_runtime_checkable
class CliDtoCreator(_Protocol):
    """Annotate the ability to launch CliDTO units"""

    def __call__(self, cls: type) -> CliDTO:
        """Produce DTO for... only cls? or general? dispatch?"""


class EventDtoFactory(_Protocol):
    """Produce the Default DTOs or their extended Versions"""

    def log(self) -> LogDTO: ...
    def cli(self) -> CliDTO: ...
    def panel(self) -> PanelDTO: ...
    def markdown(self) -> MarkdownDTO: ...
    def group(self) -> GroupDTO: ...
    def line(self) -> LineDTO: ...
    def table(self) -> TableDTO: ...
