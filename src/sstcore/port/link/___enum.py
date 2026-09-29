import enum as _e
from dataclasses import dataclass as _dataclass


@_dataclass(frozen=True, slots=True)
class _Doc:
    source: type  # the class/protocol where it was defined
    attr: str  # the attribute name
    doc: str
    origin: str  # "protocol" | "implementation"


class Event(_e.Enum):
    PROTO_DIRECT = _e.auto()
    PROTO_BASE = _e.auto()
    IMPL_DIRECT = _e.auto()
    IMPL_BASE = _e.auto()


class DocBuilder:
    def __init__(self):
        self.parts: list[str] = []
        self.seen: set[str] = set()
        self.last_event: Event | None = None

    def add(self, fragment: _Doc, event: Event) -> None:
        if fragment.doc in self.seen:
            return
        # rules based on event  sequence
        if event is Event.PROTO_BASE and self.last_event is Event.PROTO_DIRECT:
            # protocol overrode its own base — maybe skip or mark
            pass
        self.parts.append(fragment.doc)
        self.seen.add(fragment.doc)
        self.last_event = event
