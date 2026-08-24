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
    "RuleDTO",
    "TableDTO",
]

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

from ..color import Color, ColorIdentifier
from ..view import Renderable

_AlignMethod = Literal["left", "center", "right"]

# NEXT: filter out the render information


@dataclass
class LogDTO:
    message: str
    level: str = "INFO"
    metrics: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class CliDTO[ContenT: Renderable | list[Renderable]]:
    content: ContenT
    color: ColorIdentifier = Color.AZURE
    indent: int = 0
    meta: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class CliDtoCreator(Protocol):
    def __call__(self, cls: type) -> CliDTO:
        """Produce Views for the StaticFuncMeta"""


@dataclass(kw_only=True)
class GroupDTO(CliDTO[list[Renderable]]):
    """Stack renderables"""


@dataclass(kw_only=True)
class PanelDTO(CliDTO[Renderable | list[Renderable]]):
    color: str = "bold white"  # TODO: assemble stack with color+attribute
    frame: str = Color(value=2).name
    title: str | None = None
    title_align: _AlignMethod = "right"
    expand: bool = True
    padding: tuple = (0, 1)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class LineDTO(CliDTO): ...


@dataclass(kw_only=True)
class RuleDTO(CliDTO): ...


@dataclass(kw_only=True)
class MarkdownDTO(CliDTO):
    header: int = 0
    color = "white"


@dataclass(kw_only=True)
class TableDTO(CliDTO):
    """
    Store Table Data as List of Rows containing Lists of Values

     - [ 0][ 0] Top-Left Corner Element
     - [1:][1:] Content
     - [ 0][1:] Header: col_names
     - [1:][ 0] Side-titles: row_names

    """

    content: list[list[Any]]
    col_names: list[str] = field(default_factory=list)
    row_names: list[str] = field(default_factory=list)
    corner: str = ""
