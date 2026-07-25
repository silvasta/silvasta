"""Prepare EventHandler and default registry for EventBus"""

from collections.abc import Callable

from loguru import logger

from ..contract.event import Event
from ..utils.log.event_handler import handle_log_event
from ..utils.print.event_handler import handle_cli_event
from .bus import EventBus, EventHandler

type BusRegistrationFunc = Callable[[EventBus], None]


def register_default_event_handler(bus: EventBus) -> None:
    """Attach EventHandler to EventBus registry by Event- Name or Pattern"""

    bus.subscribe("*", CLI_HANDLER)  # if payload has cli=
    bus.subscribe("*", LOG_HANDLER)  # if payload has log=

    bus.subscribe_all(TELEMETRY_HANDLER)


LOG_HANDLER = EventHandler(
    name="LoguruBridge",
    func=handle_log_event,
    fail_loud=True,
)

CLI_HANDLER = EventHandler(
    name="CliPrinter",
    func=handle_cli_event,
    fail_loud=True,
)


def telemetry(event: Event):
    logger.debug(
        "Event: {event_name} | sender={sender} | keys={keys}",
        event_name=event.name,
        sender=event.sender,
        keys=list(event.payload.keys()),
    )


TELEMETRY_HANDLER = EventHandler(
    name="Telemetry",
    func=telemetry,
    fail_loud=False,
)
