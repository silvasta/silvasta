"""
Provide typed Data Transfer Objects for the EventBus

- CliDTO: Intended for __cli__ and processed by printer

"""

__all__: list[str] = [
    "PanelDTO",
    "LineDTO",
    "GroupDTO",
    "RuleDTO",
]


from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from rich.box import ROUNDED, Box

if TYPE_CHECKING:
    from ...view import Renderable
from ._cli import CliDTO

_AlignMethod = Literal["left", "center", "right"]


@dataclass(kw_only=True)
class GroupDTO(CliDTO[list[Renderable]]):
    """Stack renderables"""


@dataclass(kw_only=True)
class PanelDTO(CliDTO[Renderable | list[Renderable]]):
    # TASK: rich independant setup,
    # as well like 1 shared StyleingDTO with any needed color,frame,... arg
    color: str = "bold white"
    frame: str = "cyan"  # TODO: share normalize! done in print.mixin.layout
    title: str | None = None
    title_align: _AlignMethod = "right"
    subtitle: str | None = None
    subtitle_align: _AlignMethod = "right"
    box: Box = ROUNDED
    expand: bool = True
    padding: tuple = (0, 1)
    metrics: dict[str, Any] = field(default_factory=dict)

    # _content_field = "text"
    _strict = True  # REMOVE:


@dataclass(kw_only=True)
class LineDTO(CliDTO):
    style: str = "cyan"
    character: str = "─"


@dataclass(kw_only=True)
class RuleDTO(CliDTO):
    """Dedicated horizontal rule."""

    style: str = "cyan"
