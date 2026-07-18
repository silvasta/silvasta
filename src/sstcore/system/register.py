"""Prepare EventHandler and default registry for EventBus"""

from collections.abc import Callable
from enum import StrEnum

from loguru import logger

from ..utils.log.event_handler import handle_log_event
from ..utils.print.event_handler import handle_cli_event
from .event_bus import EventBus, EventHandler

type BusRegistrationFunc = Callable[[EventBus], None]


class SysEvent(StrEnum):  # TEST:
    LOG = "sys.log"
    WARN = "sys.warn"
    ERROR = "sys.error"


class UiEvent(StrEnum):  # TEST:
    PANEL = "ui.panel"
    TABLE = "ui.table"
    LINE = "ui.line"


def register_default_event_handler(bus: EventBus) -> None:
    """Attach EventHandler to EventBus registry by event_name"""

    # TODO: attach live monitor!?
    # bus.subscribe("sys.log", EventHandler("Monitor", self._handle_event))

    for name in ("sys.log", "sys.error", "sys.warn"):
        bus.subscribe(name, log_handler)

    for name in ("ui.panel", "ui.table", "ui.line", "ui.markdown"):
        bus.subscribe(name, cli_handler)

    bus.subscribe_all(telemetry_handler)


log_handler = EventHandler(
    name="LoguruBridge",
    func=handle_log_event,
    fail_loud=True,  # PARAM: decide defaults after tests
)

cli_handler = EventHandler(
    name="CliPrinter",
    func=handle_cli_event,
    fail_loud=True,  # PARAM: decide defaults after tests
)

telemetry_handler = EventHandler(
    name="Telemetry",
    func=lambda event: logger.debug(  # FIX: lambda as name in logs...
        "Event: {event_name} | sender={sender} | keys={keys}",
        event_name=event.name,
        sender=event.sender,
        keys=list(event.payload.keys()),
    ),
    fail_loud=True,  # PARAM: set False in sstcore/main
)
