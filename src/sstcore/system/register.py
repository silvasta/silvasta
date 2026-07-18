"""Prepare EventHandler and default registry for EventBus"""

from collections.abc import Callable
from enum import StrEnum

from loguru import logger

from ..contract.event import CliEvent, CoreEvent, DataEvent
from ..utils.log.event_handler import handle_log_event
from ..utils.print.event_handler import handle_cli_event
from .event_bus import EventBus, EventHandler

type BusRegistrationFunc = Callable[[EventBus], None]


def register_default_event_handler(bus: EventBus) -> None:
    """Attach EventHandler to EventBus registry by event_name"""

    critical_events: tuple[StrEnum, ...] = (
        DataEvent.REGISTRY_ERROR,
        DataEvent.FS_UPLOAD_ERROR,
        CoreEvent.BUS_ERROR,
        CliEvent.EXEC_FAIL,
    )
    for name in critical_events:
        bus.subscribe(name, LOG_HANDLER)

    # Send all rendering events to the Printer
    bus.subscribe("cli.render.*", CLI_HANDLER)

    # Capture ANY Warning or Error across the system
    bus.subscribe("*.*.warn", LOG_HANDLER)
    bus.subscribe("*.*.error", LOG_HANDLER)

    # Global Subscriptions
    bus.subscribe_all(TELEMETRY_HANDLER)


LOG_HANDLER = EventHandler(
    name="LoguruBridge",
    func=handle_log_event,
    fail_loud=True,  # PARAM: decide defaults after tests
)

CLI_HANDLER = EventHandler(
    name="CliPrinter",
    func=handle_cli_event,
    fail_loud=True,  # PARAM: decide defaults after tests
)

TELEMETRY_HANDLER = EventHandler(
    name="Telemetry",
    func=lambda event: logger.debug(  # FIX: lambda as name in logs...
        "Event: {event_name} | sender={sender} | keys={keys}",
        event_name=event.name,
        sender=event.sender,
        keys=list(event.payload.keys()),
    ),
    fail_loud=True,  # PARAM: set False in sstcore/main
)
