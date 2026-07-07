"""
Provide typed Data Transfer Objects for the EventBus

- CliDto for __cli__ and printer
- LogDto for __log__ and logger
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LogDTO:
    message: str
    level: str = "info"
    metrics: dict[str, Any] = field(default_factory=dict)
    # TODO: metrics is clear, but extra?
    extra: dict[str, Any] = field(default_factory=dict)


### Log
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Print

type CliDTO = PanelDTO | LineDTO | TableDTO


# AI_QUESTION: what about CliDTO as base for e.g. PanelDto(CliDTO)?
# (current approach, create type alias with all types inside .protocol)
@dataclass
class PanelDTO:
    """Provide information to render default panel (3-5 lines)"""

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

    # TODO: what is needed?
    message: str
    style: str = "white"


@dataclass
class TableDTO:
    """Provide information to render Table"""

    # TODO: what is needed?
    data: list[dict]
    headers: list[str] | None = None
