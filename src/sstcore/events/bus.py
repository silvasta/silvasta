from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Event:
    """Base payload emitted across the pipeline."""

    name: str
    sender: str  # AI: needed? (together with loguru)
    payload: dict[str, Any] = field(default_factory=dict)


type EventHandler = Callable[[Event], None]


class EventBus:
    """An execution-safe, synchronous Event Bus enabling decoupled state propagation."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._global_subscribers: list[EventHandler] = []

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Attaches a subscriber handler to a specific event identifier."""
        self._subscribers.setdefault(event_name, []).append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Attaches a subscriber intercepting all events (ideal for log tracking sinks)."""
        self._global_subscribers.append(handler)

    def emit(self, event_name: str, sender: str, **payload) -> None:
        """Fires an event to all bound subscribers."""
        event = Event(name=event_name, sender=sender, payload=payload)

        # Execute global observer (e.g. structured telemetry logging)
        for handler in self._global_subscribers:
            self._execute_safe(handler, event)

        # Execute targeted observers (e.g. printing updates, log)
        for handler in self._subscribers.get(event_name, []):
            self._execute_safe(handler, event)

    def _execute_safe(self, handler: EventHandler, event: Event) -> None:
        try:
            handler(event)
        except Exception as e:
            from loguru import logger

            logger.error(
                f"Event handler {handler.__name__} failed processing '{event.name}': {e}"
            )


bus = EventBus()  # IMPORTANT: or in cli? like config??
