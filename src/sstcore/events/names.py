# sstcore/events/names.py
import fnmatch
import re
from functools import cache
from types import SimpleNamespace


class EventName(str):
    """String-like with validation, matching, and metadata."""

    def __new__(cls, value: str, *, is_wildcard: bool = False):
        value = value.lower().strip()
        if not re.match(r"^[a-z][a-z0-9_]*(?:\.[a-z0-9_*]+)*$", value):
            raise ValueError(f"Invalid event name: {value}")
        obj = str.__new__(cls, value)
        obj.is_wildcard = is_wildcard or "*" in value
        obj.parts = value.split(".")
        return obj

    def matches(self, other: str | EventName) -> bool:
        other_str = str(other)
        if not self.is_wildcard and "*" not in other_str:  # ty: ignore
            return self == other_str
        return fnmatch.fnmatch(other_str, str(self))

    @classmethod
    @cache
    def from_string(cls, name: str) -> EventName:
        return cls(name)


Events = SimpleNamespace(
    sys=SimpleNamespace(
        log=EventName("sys.log"),
        warn=EventName("sys.warn"),
        error=EventName("sys.error"),
        ALL=EventName("sys.*", is_wildcard=True),
    ),
    ui=SimpleNamespace(
        panel=EventName("ui.panel"),
        table=EventName("ui.table"),
        line=EventName("ui.line"),
        markdown=EventName("ui.markdown"),
        ALL=EventName("ui.*", is_wildcard=True),
    ),
    ALL=EventName("*", is_wildcard=True),
)

# Convenience for validation
_KNOWN_EVENTS = {
    str(v)
    for k, v in Events.__dict__.items()
    if not k.startswith("_")
    for v in (v.__dict__.values() if hasattr(v, "__dict__") else [v])
    if isinstance(v, (str, EventName))
}


def is_known_event(name: str | EventName) -> bool:
    n = str(name)
    return n in _KNOWN_EVENTS or any("*" in p for p in n.split("."))
