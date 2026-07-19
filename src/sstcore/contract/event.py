"""
Provide Event definition, names and types

- Event: The Definition
- EmitFunc: Skeleton for exporting bus.emit functions
- EventNames: Select one to create Events, dispatch in bus to registered handler

"""

__all__: list[str] = [
    "Event",
    "EmitFunc",
    "EventPattern",
    "WildCard",
    "EventName",
    "CliEvent",
    "CoreEvent",
    "DataEvent",
]

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

type EventPattern = EventName | WildCard
type WildCard = str


@dataclass(frozen=True)
class Event:
    """Base payload emitted across the pipeline."""

    name: EventName
    sender: str
    payload: dict[str, Any] = field(default_factory=dict)


class EmitFunc(Protocol):
    def __call__(
        self, event_name: EventName, sender: str, **payload: Any
    ) -> None: ...


class EventName(StrEnum):
    """Provide clean extension point with autocomplete and typing"""


# AI: all EventNames below are just drafts so far, defaults will be created together with projects
# - for sachmis, something like SachmisEvent(EventName) could be sufficient for the beginning


class CliEvent(EventName):
    INPUT_WARN = "cli.input.warn"
    RENDER_PANEL = "cli.render.panel"
    # REMOVE: just render, and ...
    # - or better, something before
    # but panel|table is already messaged by DTO
    RENDER_TABLE = "cli.render.table"
    EXEC_FAIL = "cli.exec.error"


class CoreEvent(EventName):
    BUS_READY = "core.bus.ready"
    BUS_WARN = "core.bus.warn"
    BUS_ERROR = "core.bus.error"
    ORCHESTRATOR_INFO = "core.orchestrator.info"


class DataEvent(EventName):
    REGISTRY_INFO = "data.registry.info"
    REGISTRY_WARN = "data.registry.warn"
    REGISTRY_ERROR = "data.registry.error"

    FS_UPLOAD_SUCCESS = "data.fs.success"
    FS_UPLOAD_ERROR = "data.fs.error"
