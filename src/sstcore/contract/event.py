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
        self, event: EventName, sender: str, **payload: Any
    ) -> None: ...


class EventName(StrEnum):
    """
    Provide clean extension point with autocomplete and typing

      Pattern: "{surface}.{entity}.{action}"

    """


class CliEvent(EventName):
    RENDER = "cli.render"  # payload: PanelDTO | TableDTO | ...
    INPUT = "cli.input"  # payload: log= or cli=
    EXEC_FAIL = "cli.exec.fail"  # bridge toward process exit / ErrorHandler


class CoreEvent(EventName):
    BUS_READY = "core.bus.ready"
    BUS_DIAG = "core.bus.warn"  # one channel; level in LogDTO
    LIFECYCLE = "core.system.lifecycle"  # fixed typo
