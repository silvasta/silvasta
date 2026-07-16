"""
Provide typed Data Transfer Objects for the EventBus

- LogDTO  Intended for __log__ and processed by logger

"""

__all__: list[str] = [
    "LogSerializable",
    "LogDTO",
]

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LogSerializable(Protocol):
    def __log__(self) -> LogDTO: ...


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

    # REMOVE:??
    def to_ndjson(self) -> str:
        """For your NDJSON log monitor."""
        import json

        return json.dumps(self.to_dict())

    def __str__(self) -> str:
        """Быстрый человекочитаемый формат для отладки"""
        parts = [f"[{self.level.upper()}] {self.message}"]
        if self.metrics:
            parts.append(f"(metrics={self.metrics})")
        if self.extra:
            parts.append(f"(extra={self.extra})")
        return " ".join(parts)
