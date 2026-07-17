"""
Temporary store ideas

Usage:
    bus.emit(Events.ui.panel, sender="test", target=agent)           # str conversion automatic
    bus.subscribe(Events.sys.ANY, log_handler)                       # wildcard
    bus.subscribe(Events.ui.panel, cli_handler)

    # In a handler or ViewMixin
    if event.name == Events.ui.panel: ...
    # or: if EventName.from_string(event.name).matches(Events.ui.ANY): ...

"""

import fnmatch
import re
from functools import cache, lru_cache


class EventName(str):
    """Rich, validated, string-compatible event identifier."""

    def __new__(cls, name: str):
        name = name.lower().strip()
        if not re.match(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_*]+)*$", name):
            raise ValueError(f"Invalid event name format: {name}")
        obj = str.__new__(cls, name)
        obj.parts = name.split(".")
        obj.is_wildcard = "*" in name
        return obj

    def matches(self, pattern: str | EventName) -> bool:
        return fnmatch.fnmatch(str(self), str(pattern))

    @classmethod
    @cache
    def from_string(cls, name: str) -> EventName:
        return cls(name)


class EventNamespace:
    """Dynamic dot-access builder. Events.sys.log or Events.db.query.task."""

    def __init__(self, prefix: str = ""):
        self._prefix = prefix

    def __getattr__(self, name: str) -> EventName | EventNamespace:
        if name.startswith("_"):
            raise AttributeError(name)
        if name in ("any", "ALL", "wildcard"):
            full = f"{self._prefix}.*" if self._prefix else "*"
            return EventName(full)
        full_name = f"{self._prefix}.{name}" if self._prefix else name
        return (
            EventNamespace(full_name)
            if name in ("sys", "ui", "db", "bus")
            else EventName(full_name)
        )

    def __str__(self) -> str:
        return self._prefix or "root"

    def __repr__(self) -> str:
        return f"Events.{self._prefix}" if self._prefix else "Events"


Events = EventNamespace()

# Registry for warnings (populated at import or bootstrap)
_KNOWN = set()  # populated by register_default_event_handler or decorators


@lru_cache(maxsize=256)
def matches_any_pattern(event_name: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(event_name, p) for p in patterns)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### MOVE TO BUS WHEN USED!
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


# from .names import EventName, Events
class EventBus:
    """TEST"""

    # ... existing __init__, subscribe, subscribe_all ...

    # def _get_event_subscribers(self, event_name: str) -> list[EventHandler]:
    #     """Support exact matches + wildcards via fnmatch (cached)."""
    #     return self._match_subscribers(event_name)

    # @lru_cache(maxsize=512)
    # def _match_subscribers(self, event_name: str) -> list[EventHandler]:
    #     matched: list[EventHandler] = []
    #     for pattern, handlers in self._subscribers.items():
    #         if fnmatch.fnmatch(event_name, pattern) or fnmatch.fnmatch(
    #             pattern, event_name
    #         ):
    #             matched.extend(handlers)
    #     return matched
    #
    # def emit(
    #     self, event_name: str | EventName, sender: str, **payload: Any
    # ) -> None:
    #     name_str = str(event_name)
    #     if (
    #         not Events.is_known_event(name_str) and "*" not in name_str
    #     ):  # from simple version
    #         logger.warning(
    #             f"Unknown event emitted: {name_str} (sender={sender})"
    #         )
    #     # ... rest unchanged, create Event(name=name_str, ...)
