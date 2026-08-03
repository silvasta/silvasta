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
from typing import Any, Literal

from rich.box import ROUNDED, Box

from ._cli import CliDTO, Renderable

# LATER: move function implementation out of the port

_AlignMethod = Literal["left", "center", "right"]

# NEXT: content: Renderable


@dataclass(kw_only=True)
class GroupDTO(CliDTO):
    # TODO: remove CliDTO?
    # or ensure the args here can be set like global for all sub dtos
    """Ordered stack of renderables (vertical by default)."""

    items: list[CliDTO] = field(default_factory=list)
    title: str | None = None
    # layout: Literal["vertical", "horizontal"] = "vertical"
    _content_field = "items"


@dataclass(kw_only=True)
class PanelDTO(CliDTO):
    text: Renderable | list[Renderable]  # TODO: check when to normalize
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

    _content_field = "text"
    _strict = True


@dataclass(kw_only=True)
class LineDTO(CliDTO):
    text: str | None = None  # For Rule = just line ----
    style: str = "cyan"
    character: str = "─"
    _content_field = "text"
    _strict = True


@dataclass(kw_only=True)
class RuleDTO(CliDTO):
    """Dedicated horizontal rule."""

    char: str = "─"
    style: str = "cyan"
    _content_field = "char"
    _strict = False
