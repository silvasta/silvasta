"""Create base infrastructure for events"""

import fnmatch
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from loguru import logger

from ..contract.system import EventProtocol


@dataclass(frozen=True)
# IDEA: move this to contract? forget about protocol and use real Event?
class Event:
    """Base payload emitted across the pipeline."""

    name: str
    sender: str
    payload: dict[str, Any] = field(default_factory=dict)


if TYPE_CHECKING:  # --- SYNCHRONIZATION GUARD ---
    # Ensure that EventProtocol always matches Event!
    _: EventProtocol = Event(name="", sender="", payload={})


@dataclass(frozen=True)
class EventHandler:
    """Process Events from the bus in observable Environment"""

    name: str
    func: Callable[[Event], None]
    fail_loud: bool = False

    def __str__(self) -> str:
        return f"EventHandler[{self.name}]"  # LATER: check events.view

    def __call__(self, event: Event) -> None:
        """Execute handler function and manage fail if flag is set"""
        try:
            self.func(event)
        except Exception as error:
            if self.fail_loud:  # LATER: custom error?
                raise RuntimeError(f"Critical Fail: {self}") from error

            # TASK: ensure handler fails are proper logged
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

    # IDEA: log(LogDTO args) -> LogDTO

    def emit(self, event_name: str, sender: str, **payload) -> None:
        """Fire an Event to all global and event-specific subscribers"""

        event = Event(name=event_name, sender=sender, payload=payload)

        for handler in self._global_subscribers:  # structured telemetry, ...
            handler(event)

        for handler in self._get_event_subscribers(event_name):
            handler(event)

    def _get_event_subscribers(self, event_name: str) -> list[EventHandler]:
        """Filter specific subscribers by name LATER: by wildcard"""
        return self._subscribers.get(event_name, [])

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Different Ideas
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def _get_event_subscribers1(self, event_name: str) -> list[EventHandler]:
        return self._match_subscribers(event_name)

    # @lru_cache(maxsize=256)
    def _match_subscribers(self, event_name: str) -> list[EventHandler]:

        matched_handlers: list[EventHandler] = []
        for pattern, handlers in self._subscribers.items():
            if fnmatch.fnmatch(event_name, pattern):
                matched_handlers.extend(handlers)
        return matched_handlers

    # IDEA: why not just using the enum/datastructre for that?

    def _get_event_subscribers2(self, event_name: str) -> list[EventHandler]:
        handlers = self._subscribers.get(event_name, []).copy()

        # Check wildcards based on namespace (e.g., event "sys.log" matches wildcard "sys.*")
        namespace = event_name.split(".")[0]
        wildcard = f"{namespace}.*"
        handlers.extend(self._subscribers.get(wildcard, []))

        return handlers

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### NAMES
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# from .names import EventName, Events  # or your chosen approach
#
#
# class _EventBus:
#     # ... existing __init__, subscribe, subscribe_all ...
#
#     def _get_event_subscribers(self, event_name: str) -> list[EventHandler]:
#         """Support exact matches + wildcards via fnmatch (cached)."""
#         return self._match_subscribers(event_name)
#
#     # @lru_cache(maxsize=512)
#     def _match_subscribers(self, event_name: str) -> list[EventHandler]:
#         matched: list[EventHandler] = []
#         for pattern, handlers in self._subscribers.items():  # ty:ignore
#             if fnmatch.fnmatch(event_name, pattern) or fnmatch.fnmatch(
#                 pattern, event_name
#             ):
#                 matched.extend(handlers)
#         return matched
#
#     def emit(
#         self, event_name: str | EventName, sender: str, **payload: Any
#     ) -> None:
#         name_str = str(event_name)
#         if (
#             not Events.is_known_event(name_str) and "*" not in name_str
#         ):  # from simple version
#             logger.warning(
#                 f"Unknown event emitted: {name_str} (sender={sender})"
#             )
#         # ... rest unchanged, create Event(name=name_str, ...)
