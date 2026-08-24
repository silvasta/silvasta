"""
Define the Structure of EventNames and provide Defaults

EventNames:
- Create Event with selected Name
- Register Handler in Bus with Pattern
  (Pattern is EventName including WildCard)
- Dispatch by Bus at Runtime

  Pattern:  "{surface}.{entity}.{action}"
  Wildcard: "{surface|*}.{entity|*}.{action|*}"

"""

__all__: list[str] = [
    "EventName",
    "EventPattern",
    "WildCard",
    #
    "CliEvent",
    "CoreEvent",
]

from enum import StrEnum as _StrEnum

type EventPattern = EventName | WildCard
type WildCard = str


class EventName(_StrEnum):
    """Provide clean extension point with autocomplete and typing"""


class CliEvent(EventName):
    """Use Payload (log=... or cli=...) for dispatch to Printer/Loguru"""

    RENDER = "cli.render"
    INPUT = "cli.input"
    EXEC_FAIL = "cli.exec.fail"


class CoreEvent(EventName):
    BUS_READY = "core.bus.ready"
    BUS_DIAG = "core.bus.warn"
    LIFECYCLE = "core.system.lifecycle"
