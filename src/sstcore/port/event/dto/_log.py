"""
Provide typed Data Transfer Objects for the EventBus

- LogDTO  Intended for __log__ and processed by logger

"""

from dataclasses import dataclass, field
from typing import Any

__all__: list[str] = [
    "LogDTO",
]

from ._base import EventDTO


@dataclass
class LogDTO(EventDTO):
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
