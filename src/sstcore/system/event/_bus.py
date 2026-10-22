"""
Provide Infrastructure for Events

- EventBus: Route Events by name to registered EventHandling
- XXX EventHandling: Process Event with optional Error handling
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "Bus",
]

import fnmatch
from functools import lru_cache
from typing import TYPE_CHECKING, Self, Unpack

from ...brick.reflect import clsname
from ...port.event import Event, EventBus, EventHandling
from ...port.event.name import CoreEvent, EventName, EventPattern
from ...port.link import portlink
from ...port.system import BusInput, BusLoader, BusSpec
from ._handler import register_default_event_handler


@portlink(EventBus)
class Bus:
    def __init__(self) -> None:
        self._subscribers: dict[EventPattern, list[EventHandling]] = {}
        self._global_subscribers: list[EventHandling] = []

    def emit(self, event: EventName, /, sender: str, **payload) -> None:

        core_event = Event(name=event, sender=sender, payload=payload)

        for handler in self._global_subscribers:
            handler(core_event)

        for handler in self._match_subscribers(event):
            handler(core_event)

    def subscribe(self, name: EventPattern, handler: EventHandling) -> None:
        self._subscribers.setdefault(name, []).append(handler)

    def subscribe_all(self, handler: EventHandling) -> None:
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

    def _match_subscribers(self, event: EventName) -> tuple[EventHandling, ...]:
        """Filter subscribers by event name and wildcard pattern"""

        subscribers: tuple[EventPattern, ...] = tuple(self._subscribers.keys())

        matched_handlers: list[EventHandling] = [
            handler
            for pattern in _get_patterns(event, subscribers)
            for handler in self._subscribers[pattern]
        ]

        return tuple(dict.fromkeys(matched_handlers))

    # IMPORTANT: @portlink(BusLoader)
    # TASK: portlink.func?
    # - this but for methods instead of classes!
    @classmethod
    def ready(cls, **data: Unpack[BusInput]) -> Self:

        bus: Self = cls()
        spec = BusSpec(**data)

        if spec.use_default_registration:
            register_default_event_handler(bus)

        if spec.bus_registration:
            spec.bus_registration(bus)

        bus.emit(
            CoreEvent.BUS_DIAG,
            sender=f"{bus}",
            log="EventBus setup complete",
        )
        return bus


@lru_cache(maxsize=256)
def _get_patterns(
    event: EventName, active_patterns: tuple[EventPattern, ...]
) -> tuple[EventPattern, ...]:  # tuple for lru_cache (immutable)
    """Match pattern and cache results decoupled from the Bus"""
    return tuple(
        pattern
        for pattern in active_patterns
        if fnmatch.fnmatch(event, pattern)
    )


if TYPE_CHECKING:
    _loader: BusLoader = Bus.ready
    _instance_check: EventBus = Bus()
    _class_check: type[EventBus] = Bus
