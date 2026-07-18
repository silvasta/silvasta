"""Create base infrastructure for events"""

__all__: list[str] = [
    "EventHandler",
    "EventBus",
]

import fnmatch
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache

from loguru import logger

from ..contract.event import Event


@dataclass(frozen=True)
class EventHandler:
    """Process Events from the bus in observable Environment"""

    name: str
    func: Callable[[Event], None]
    fail_loud: bool = False

    def __str__(self) -> str:
        return f"EventHandler[{self.name}]"

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
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._global_subscribers: list[EventHandler] = []

    def subscribe_all(self, handler: EventHandler) -> None:
        """Attach global handler as subscriber to all events"""
        self._global_subscribers.append(handler)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Attach handler as subscriber to specific event"""
        self._subscribers.setdefault(event_name, []).append(handler)

    def emit(self, event_name: str, sender: str, **payload) -> None:
        """Fire an Event to all global and event-specific subscribers"""

        # WARN: validation payload?
        event = Event(name=event_name, sender=sender, payload=payload)

        for handler in self._global_subscribers:
            handler(event)

        for handler in self._get_event_subscribers(event_name):
            handler(event)

    def _get_event_subscribers(self, event_name: str) -> list[EventHandler]:
        """Filter specific subscribers by name LATER: by wildcard"""
        return self._subscribers.get(event_name, [])

    def _match_subscribers(self, event_name: str) -> tuple[EventHandler, ...]:
        """Filter subscribers by wildcard pattern."""

        matched_patterns: tuple[str, ...] = _get_matching_patterns(
            event_name, tuple(self._subscribers.keys())
        )  # tuple is hashable -> needed for lru_cache

        matched_handlers: list[EventHandler] = []
        for pattern in matched_patterns:
            matched_handlers.extend(self._subscribers[pattern])

        # remove duplicates while preserving order
        return tuple(dict.fromkeys(matched_handlers))


@lru_cache(maxsize=256)
def _get_matching_patterns(
    event_name: str, active_patterns: tuple[str, ...]
) -> tuple[str, ...]:
    """Execute and especially Cache decoupled from the Bus"""
    return tuple(p for p in active_patterns if fnmatch.fnmatch(event_name, p))
