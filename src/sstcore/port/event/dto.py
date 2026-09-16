"""
Define the Event DTOs for Log and Print

- LogDTO  Intended for __log__ and processed by Loguru.logger
- CliDTO: Intended for __cli__ and processed by printer

Rendering Protocols with Runtime check
- LogSerializable
- CliRenderable
                                                 DependencyLevel[0]
                                                 (inside event)
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
    # views
    "LogSerializable",
    "CliRenderable",
]

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from typing import Any as _Any
from typing import Literal as _Literal
from typing import Protocol as _Protocol
from typing import runtime_checkable as _runtime_checkable

from ..calling import Richable as _Richable
from ..color import Color as _Color
from ..color import ColorIdentifier as _ColorIdentifier

type _Renderable = str | CliRenderable | _Richable

_AlignMethod = _Literal["left", "center", "right"]


@_dataclass
class LogDTO:
    """Main (and only) Member of the Log Pipeline"""

    message: str
    level: str = "INFO"
    metrics: dict[str, _Any] = _field(default_factory=dict)
    extra: dict[str, _Any] = _field(default_factory=dict)


# TASK: filter out the to much render information
@_dataclass
class CliDTO[ContenT: _Renderable | list[_Renderable]]:
    """Root of the Cli Pipeline"""

    content: ContenT
    color: _ColorIdentifier = _Color.AZURE
    indent: int = 0
    meta: dict[str, _Any] = _field(default_factory=dict)


@_runtime_checkable
class CliDtoCreator(_Protocol):
    """Annotate the ability to launch CliDTO units"""

    def __call__(self, cls: type) -> CliDTO:
        """Produce DTO for... only cls? or general? dispatch?"""


@_dataclass(kw_only=True)
class PanelDTO(CliDTO[_Renderable | list[_Renderable]]):
    # TODO: assemble stack with color+attribute
    color: str = "bold white"
    frame: str = _Color(value=2).name
    title: str | None = None
    # TASK: filter out the to much render information
    title_align: _AlignMethod = "right"
    expand: bool = True
    padding: tuple = (0, 1)
    metrics: dict[str, _Any] = _field(default_factory=dict)


@_dataclass(kw_only=True)
class MarkdownDTO(CliDTO):
    header: int = 0


@_dataclass(kw_only=True)
class LineDTO(CliDTO): ...


@_dataclass(kw_only=True)
class GroupDTO(CliDTO[list[_Renderable]]):
    """Stack multiple renderable Views"""


@_dataclass(kw_only=True)
class TableDTO(CliDTO):
    """
    Store Table Data as List of Rows containing Lists of Values

     - [1:][1:] Main content
     - [ 0][1:] Header: col_names
     - [1:][ 0] Sidebar: row_names
     - [ 0][ 0] Top-left element

    """

    # TASK: filter out the to much render information

    content: list[list[_Any]]
    col_names: list[str] = _field(default_factory=list)
    row_names: list[str] = _field(default_factory=list)
    corner: str = ""


#  LINE: -- RenderProtocols with Runtime check -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_runtime_checkable
class CliRenderable(_Protocol):
    def __cli__(self) -> CliDTO: ...


@_runtime_checkable
class LogSerializable(_Protocol):
    def __log__(self) -> LogDTO: ...
