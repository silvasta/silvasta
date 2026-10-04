"""
Define the Structure of the Event Data and Pipeline

                              DependencyLevel.sstcore.port.event[1]
"""

__all__: list[str] = [
    "Event",
    "EventHandler",
    "EventBus",
    "BusRegistration",
]

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol, Self

from .name import EventName, EventPattern

type BusRegistration = Callable[[EventBus], None]


@dataclass(frozen=True)
class Event:
    """Base payload emitted across the pipeline."""

    name: EventName
    sender: str
    payload: dict[str, Any] = field(default_factory=dict)


class EventHandler(Protocol):
    def __call__(self, event: Event) -> None:
        """Process emitted Events dispatched by the Bus"""


class EventBus(Protocol):
    """Enable decoupled state propagation for synchronous Events"""

    def emit(self, event_name: EventName, sender: str, **payload: Any) -> None:
        """Fire an Event to all global and event-specific subscribers"""

    def subscribe(self, name: EventPattern, handler: EventHandler) -> None:
        """Attach handler as subscriber to specific event"""

    def subscribe_all(self, handler: EventHandler) -> None:
        """Attach global handler as subscriber to all events"""

    @classmethod
    def ready(cls) -> Self:
        """Load EventBus explicit as one-time initialization"""
