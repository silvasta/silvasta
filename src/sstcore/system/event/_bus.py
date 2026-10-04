"""
Provide Infrastructure for Events

- EventBus: Route Events by name to registred EventHandler
- XXX EventHandler: Process Event with optional Error handling
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "Bus",
]

import fnmatch
from functools import lru_cache
from typing import TYPE_CHECKING, Self, Unpack

from ...brick.labor import clsname
from ...port.event import Event, EventBus, EventHandler
from ...port.event.name import CoreEvent, EventName, EventPattern
from ...port.link import portlink
from ...port.system import BusData, BusInput, BusLoader
from ._handler import register_default_event_handler


@portlink(EventBus)
class Bus:
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
        return clsname(self)

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
    def ready(cls, **data: Unpack[BusInput]) -> Self:
        """Load EventBus explicit as one-time initialization"""

        spec = BusData(**data)
        bus: Self = cls()

        if spec.use_default_registration:
            register_default_event_handler(bus)

        if spec.bus_registration:
            spec.bus_registration(bus)

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
    _loader: BusLoader = Bus.ready
    _instance_check: EventBus = Bus()
    _class_check: type[EventBus] = Bus
