"""
Provide Infrastructure for Events

- EventBus: Route Events by name to registred EventHandler
- XXX EventHandler: Process Event with optional Error handling
                                                       DependencyLevel[1]
"""

from typing import TYPE_CHECKING, Self

__all__: list[str] = [
    "EventBus",
]

import fnmatch
from functools import lru_cache

from ...brick.format import cls_name
from ...port.event import BusRegistration, Event, EventHandler
from ...port.event import EventBus as EventBus_
from ...port.event.name import CoreEvent, EventName, EventPattern
from ._handler import register_default_event_handler


class EventBus:
    """Enable decoupled state propagation for synchronous Events"""

    def __init__(self) -> None:
        self._subscribers: dict[EventPattern, list[EventHandler]] = {}
        self._global_subscribers: list[EventHandler] = []

    def emit(self, event_name: EventName, sender: str, **payload) -> None:
        """Fire an Event to all global and event-specific subscribers"""

        event = Event(name=event_name, sender=sender, payload=payload)

        for handler in self._global_subscribers:
            handler(event)

        for handler in self._match_subscribers(event_name):
            handler(event)

    def subscribe(self, name: EventPattern, handler: EventHandler) -> None:
        """Attach handler as subscriber to specific event"""
        self._subscribers.setdefault(name, []).append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Attach global handler as subscriber to all events"""
        self._global_subscribers.append(handler)

    @property
    def n_handler(self) -> int:
        return len(self._subscribers)

    @property
    def n_global_handler(self) -> int:
        return len(self._global_subscribers)

    def __str__(self) -> str:
        return cls_name(self)

    def __repr__(self) -> str:
        return f"{self}(  {self.n_global_handler} 󰌌 {self.n_handler} 󰍹 )"

    def _match_subscribers(
        self, event_name: EventName
    ) -> tuple[EventHandler, ...]:
        """Filter subscribers by event name and wildcard pattern"""

        subscribers: tuple[EventPattern, ...] = tuple(self._subscribers.keys())

        matched_handlers: list[EventHandler] = [
            handler
            for pattern in _get_patterns(event_name, subscribers)
            for handler in self._subscribers[pattern]
        ]

        return tuple(dict.fromkeys(matched_handlers))

    @classmethod
    def bootstrap(
        cls,
        bus_registration: BusRegistration | None = None,
        use_default_registration=True,
    ) -> Self:
        """Load EventBus explicit as one-time initialization"""
        bus: Self = cls()

        if use_default_registration:
            register_default_event_handler(bus)

        if bus_registration:
            bus_registration(bus)

        bus.emit(
            event_name=CoreEvent.BUS_DIAG,
            sender="BusSetup",
            log="EventBus setup complete",
        )
        return bus


@lru_cache(maxsize=256)
def _get_patterns(
    event_name: EventName, active_patterns: tuple[EventPattern, ...]
) -> tuple[EventPattern, ...]:  # tuple for lru_cache (immutable)
    """Match pattern and cache results decoupled from the Bus"""
    return tuple(
        pattern
        for pattern in active_patterns
        if fnmatch.fnmatch(event_name, pattern)
    )


if TYPE_CHECKING:
    _instance_check: EventBus_ = EventBus()
    _class_check: type[EventBus_] = EventBus
