from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from loguru import logger  # IDEA: use Python 3.15 lazy load? check decouple

type BusRegistrationFunc = Callable[[EventBus], None]


@dataclass(frozen=True)
class Event:
    """Base payload emitted across the pipeline."""

    name: str
    sender: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EventHandler:
    """Process Events from the bus in observable Environment"""

    name: str
    func: Callable[[Event], None]
    fail_loud: bool = False

    def __str__(self) -> str:
        return f"EventHandler[{self.name}]"  # LATER: check events.view

    # NEXT: check separate: EventHandler.__call__ and EventHandler.safe_execute

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

    # AI_TASK: decorator for attach, here and|or System?

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._global_subscribers: list[EventHandler] = []

    def subscribe_all(self, handler: EventHandler) -> None:
        """Attach global handler as subscriber to all events"""
        self._global_subscribers.append(handler)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Attach handler as subscriber to specific event"""
        self._subscribers.setdefault(event_name, []).append(handler)

    def _get_event_subscribers(self, event_name: str) -> list[EventHandler]:
        """Filter specific subscribers by name LATER: by wildcard"""
        # TODO: how to filter for example "ui.*"?
        # -> first define wildcard strategy: "name.*"
        # -> then find solution here
        return self._subscribers.get(event_name, [])

    def emit(self, event_name: str, sender: str, **payload) -> None:
        """Fire an Event to all global and event-specific subscribers"""

        event = Event(name=event_name, sender=sender, payload=payload)

        for handler in self._global_subscribers:  # structured telemetry, ...
            handler(event)

        for handler in self._get_event_subscribers(event_name):
            handler(event)
