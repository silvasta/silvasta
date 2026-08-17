"""
Provide typed Data Transfer Objects for the EventBus

- CliDTO: Intended for __cli__ and processed by printer

"""

# LATER: move function implementation out of the port

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

# NEXT: content: Renderable


@dataclass(kw_only=True)
class GroupDTO(CliDTO[list[Renderable]]):
    """Stack renderables"""

    # REMOVE: (after transform) items: list[CliDTO] = field(default_factory=list)
    title: str | None = None
    # LATER: check if this makes sense
    # layout: Literal["vertical", "horizontal"] = "vertical"
    # REMOVE: (after transform) _content_field = "items"


@dataclass(kw_only=True)
class PanelDTO(CliDTO[Renderable | list[Renderable]]):
    # text: Renderable | list[Renderable]  # TODO: check when to normalize
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
    _strict = (
        True  # AI_QUESTION: is this a toggle for all CliDTO? or all PanelDTO?
    )


@dataclass(kw_only=True)
class LineDTO(CliDTO):
    # text: str | None = None  # For Rule = just line ----
    style: str = "cyan"
    character: str = "─"
    # _content_field = "text"
    # _strict = True


@dataclass(kw_only=True)
class RuleDTO(CliDTO):
    """Dedicated horizontal rule."""

    # char: str = "─"
    style: str = "cyan"
    # _content_field = "char"
    # _strict = False
