from dataclasses import dataclass
from typing import Any

from ..contract.event import EventName
from ..contract.log import LogDTO
from .bus import EventBus

# AI: Basic idea of exporting a powerful emitter is nice,
# but this here completely abandons the main Emitter

# AI_TASK: extract useful pattern


@dataclass(frozen=True)
class BoundEmitter:
    """A contextual emitter that remembers 'who' is sending and 'what' the default routing is."""

    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:

    bus: EventBus
    sender: str
    default_event: EventName

    def __call__(self, event_name: EventName, **payload: Any) -> None:
        self.bus.emit(event_name, self.sender, **payload)

    def log(
        self,
        message: str,
        level: str = "INFO",
        event: EventName | None = None,
        **extra: Any,
    ):
        dto = LogDTO(message=message, level=level, extra=extra)
        self(event or self.default_event, log=dto)

    def info(self, message: str, **extra):
        self.log(message, "INFO", **extra)

    def warning(self, message: str, **extra):
        self.log(message, "WARNING", **extra)

    def error(self, message: str, **extra):
        self.log(message, "ERROR", **extra)

    def success(self, message: str, **extra):
        self.log(message, "SUCCESS", **extra)

    def view(self, target: Any, event: EventName | None = None) -> None:
        """Automatically extract LogDTO and CliDTO from objects implementing the protocols."""
        payload = {"target": target}

        if hasattr(target, "__log__"):
            payload["log"] = target.__log__()
        elif hasattr(target, "message"):
            payload["log"] = LogDTO(message=str(target), level="INFO")

        if hasattr(target, "__cli__"):
            payload["cli"] = target.__cli__()

        self(event or self.default_event, **payload)


@dataclass(frozen=True)
class Emitter:
    bus: EventBus

    # NEXT:
    # NEXT:
    def bind(self, sender: str, default_event: EventName) -> BoundEmitter:
        """Factory to create a context-aware emitter for a specific class instance."""
        return BoundEmitter(self.bus, sender, default_event)
