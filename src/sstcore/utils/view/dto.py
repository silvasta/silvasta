"""
Provide typed DataTransferObjects for the EventBus

- CliDTO: Intended for __cli__ and processed by printer
- LogDTO  Intended for __log__ and processed by logger

"""

from dataclasses import dataclass, field
from typing import Any

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


### Print
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Log


@dataclass
class LogDTO:
    message: str
    level: str = "INFO"
    metrics: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Provide clean dictionary for log injection"""
        return {
            "message": self.message,
            "level": self.level.upper(),
            **self.metrics,
            **self.extra,
        }
