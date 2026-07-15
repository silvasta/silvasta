"""
Provide typed Data Transfer Objects for the EventBus

- CliDTO: Intended for __cli__ and processed by printer

"""

__all__: list[str] = [
    "CliRenderable",
    "CliDTO",
    "PanelDTO",
    "LineDTO",
    "TableDTO",
]

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CliRenderable(Protocol):
    def __cli__(self) -> CliDTO: ...


type CliDTO = PanelDTO | LineDTO | TableDTO


@dataclass
class PanelDTO:
    """Provide information to render default panel (3-5 lines)"""

    def __cli__(self) -> CliDTO:
        return self

    # TODO: select best subset
    title: str
    content: str | list[str]
    metrics: dict[str, Any] = field(default_factory=dict)
    color: str = "cyan"
    frame: str = "cyan"
    subtitle: str | None = None


# TASK: think about strategy for color and style handover
# - probably this is anyway handled by the rendering based on state
# - still some objects might have preferences for some details


@dataclass
class LineDTO:
    """Provide information to render single line"""

    def __cli__(self) -> CliDTO:
        return self

    # TODO: what is needed?
    message: str
    style: str = "white"


@dataclass
class TableDTO:
    """Provide structured dataset to render beautiful tables."""

    def __cli__(self) -> CliDTO:
        return self

    # FIX: create proper table setup
    data: list[dict[str, Any] | list[Any]]
    headers: list[str] | None = None
    title: str | None = None
    style: str = "cyan"
