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
    #
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
    RENDER = "cli.render"  # payload: PanelDTO | TableDTO | ...
    INPUT = "cli.input"  # payload: log= or cli=
    EXEC_FAIL = "cli.exec.fail"  # bridge toward process exit / ErrorHandler


class CoreEvent(EventName):
    BUS_READY = "core.bus.ready"
    BUS_DIAG = "core.bus.warn"  # one channel; level in LogDTO
    LIFECYCLE = "core.system.lifecycle"
