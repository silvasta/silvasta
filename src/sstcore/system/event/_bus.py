"""
Provide Infrastructure for Events

- EventBus: Route Events by name to registred EventHandler
- EventHandler: Process Event with optional Error handling
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "EventBus",
    "EventHandler",
]

import fnmatch
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache

from loguru import logger

from ...port.event import Event, EventName, EventPattern


@dataclass(frozen=True)
class EventHandler:
    """Process Events emmited from the bus in observable Environment"""

    name: str
    func: Callable[[Event], None]
    fail_loud: bool = False

    def __str__(self) -> str:
        return f"EventHandler[{self.name}]"

    # LATER: think about generic
    # - synchronize with ErrorHandler

    def __call__(self, event: Event) -> None:
        """Execute handler function and manage fail if flag is set"""
        try:
            self.func(event)
        except Exception as error:
            if self.fail_loud:  # LATER: custom error?
                raise RuntimeError(f"Critical Fail: {self}") from error

            logger.error(f"{self} failed for '{event.name}': {error}")
            logger.debug(f"Traceback for {self}:", exc_info=True)


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
        return type(self).__name__

    def __repr__(self) -> str:  # TEST:
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


@lru_cache(maxsize=256)
def _get_patterns(
    event_name: EventName, active_patterns: tuple[EventPattern, ...]
) -> tuple[EventPattern, ...]:
    """Match pattern and cache results decoupled from the Bus"""
    return tuple(
        pattern
        for pattern in active_patterns
        if fnmatch.fnmatch(event_name, pattern)
    )
