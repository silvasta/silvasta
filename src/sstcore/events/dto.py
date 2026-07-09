"""
Provide typed DataTransferObjects for the EventBus

- CliDto for __cli__ and printer
- LogDto for __log__ and logger
"""

# TASK: resolve this to -> log|print?

from dataclasses import dataclass, field
from typing import Any


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


### Log
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Print

type CliDTO = PanelDTO | LineDTO | TableDTO


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

    # FIX: create proper Table setup
    data: list[dict]
    headers: list[str] | None = None
