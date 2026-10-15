"""
Define the Structure of the Event Data and Pipeline

                              DependencyLevel.sstcore.port.event[1]
"""

__all__: list[str] = [
    "Event",
    "EventBus",
    "EventHandling",
    "BusRegistration",
]

from dataclasses import dataclass, field
from typing import Any, Protocol, Self

from .name import EventName, EventPattern


@dataclass(frozen=True)
class Event:
    """Base payload emitted across the pipeline."""

    name: EventName
    sender: str
    payload: dict[str, Any] = field(default_factory=dict)


class EventHandling(Protocol):
    # TASK: Functor as direct input instead of func?
    # - check when func is ever needed
    def __call__(self, event: Event) -> None:
        """Process emitted Events dispatched by the Bus"""


class BusRegistration(Protocol):
    def __call__(self, bus: EventBus) -> None:
        """Subscribe EventHandling by EventName or Wildcard to EventBus"""


class EventBus(Protocol):
    """Enable decoupled state propagation for synchronous Events"""

    def emit(self, event: EventName, sender: str, /, **payload: Any) -> None:
        """Fire an Event to all global and event-specific subscribers"""

    def subscribe(self, name: EventPattern, handler: EventHandling) -> None:
        """Attach handler as subscriber to specific event"""

    def subscribe_all(self, handler: EventHandling) -> None:
        """Attach global handler as subscriber to all events"""

    @classmethod
    def ready(cls) -> Self:
        """Load EventBus explicit as one-time initialization"""
