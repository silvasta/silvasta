"""
Define the Structure of the Event and its Pipeline

-
"""

from ._emit import BusEmit

__all__: list[str] = [
    "Event",
    "EventHandler",
    "EventBus",
    "BusRegistration",
]

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

from .name import EventName, EventPattern

type BusRegistration = Callable[[EventBus], None]


@dataclass(frozen=True)
class Event:
    """Base payload emitted across the pipeline."""

    name: EventName
    sender: str
    payload: dict[str, Any] = field(default_factory=dict)


class EventHandler(Protocol):
    def __call__(self, event: Event) -> None: ...


class EventBus(Protocol):
    def emit(
        self, event_name: EventName, sender: str, **payload: Any
    ) -> None: ...
    def subscribe(self, name: EventPattern, handler: EventHandler) -> None: ...
    def subscribe_all(self, handler: EventHandler) -> None: ...


if TYPE_CHECKING:
    _e: BusEmit = EventBus.emit
