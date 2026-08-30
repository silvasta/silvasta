"""
Define the Event DTOs for Log and Print

- LogDTO  Intended for __log__ and processed by Loguru.logger
- CliDTO: Intended for __cli__ and processed by printer

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

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

from ..color import Color, ColorIdentifier
from ..view import Renderable

_AlignMethod = Literal["left", "center", "right"]

# NEXT: filter out the here unneeded render information


@dataclass
class LogDTO:
    """Main (and only) Member of the Log Pipeline"""

    message: str
    level: str = "INFO"
    metrics: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class CliDtoCreator(Protocol):
    """Produce Views for the StaticFuncMeta"""

    def __call__(self, cls: type) -> CliDTO: ...


@dataclass
class CliDTO[ContenT: Renderable | list[Renderable]]:
    """Root of the Cli Pipeline"""

    content: ContenT
    color: ColorIdentifier = Color.AZURE
    indent: int = 0
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class PanelDTO(CliDTO[Renderable | list[Renderable]]):
    # TODO: assemble stack with color+attribute
    color: str = "bold white"
    frame: str = Color(value=2).name
    title: str | None = None
    # NEXT: detach to much information somehow
    title_align: _AlignMethod = "right"
    expand: bool = True
    padding: tuple = (0, 1)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class MarkdownDTO(CliDTO):
    header: int = 0


@dataclass(kw_only=True)
class LineDTO(CliDTO): ...


@dataclass(kw_only=True)
class GroupDTO(CliDTO[list[Renderable]]):
    """Stack multiple renderable Views"""


@dataclass(kw_only=True)
class TableDTO(CliDTO):
    """
    Store Table Data as List of Rows containing Lists of Values

     - [1:][1:] Main content
     - [ 0][1:] Header: col_names
     - [1:][ 0] Sidebar: row_names
     - [ 0][ 0] Top-left element

    """

    content: list[list[Any]]
    col_names: list[str] = field(default_factory=list)
    row_names: list[str] = field(default_factory=list)
    corner: str = ""
