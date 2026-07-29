"""
Provide typed Data Transfer Objects for the EventBus

- LogDTO  Intended for __log__ and processed by logger

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "LogSerializable",
    "LogDTO",
]

from dataclasses import dataclass, field
from typing import Any, Protocol, Self, runtime_checkable


@runtime_checkable
class LogSerializable(Protocol):
    def __log__(self) -> LogDTO: ...


class _DtoBase:  # IDEA: __cli__? check with printer.render
    def __log__(self) -> Self:
        return self

    def __str__(self) -> str:
        return type(self).__name__


@dataclass
class LogDTO(_DtoBase):
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
