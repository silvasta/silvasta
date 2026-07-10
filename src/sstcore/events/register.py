"""
Prepare EventHandler and default subscriptions for EventBus

- cli
- log
- telemetry

"""  # TODO:

from collections.abc import Callable

from loguru import logger

# IDEA: use Python 3.15 lazy load? check decouple
from ..utils.log.event_handler import handle_log_event
from ..utils.print.event_handler import handle_cli_event
from .bus import EventBus, EventHandler

type BusRegistrationFunc = Callable[[EventBus], None]


# LATER: develeop system for event_names
def register_default_event_handler(bus: EventBus) -> None:
    """Attach EventHandler to EventBus registry by event_name"""

    for name in ("sys.log", "sys.error", "sys.warn"):
        bus.subscribe(name, log_handler)

    for name in ("ui.panel", "ui.table", "ui.line", "ui.markdown"):
        bus.subscribe(name, cli_handler)

    bus.subscribe_all(telemetry_handler)


log_handler = EventHandler(
    name="LoguruBridge",
    func=handle_log_event,
    fail_loud=True,  # PARAM: check after test
)

cli_handler = EventHandler(
    name="CliPrinter",
    func=handle_cli_event,
    fail_loud=True,  # PARAM: check after test
)

telemetry_handler = EventHandler(
    name="telemetry",
    func=lambda event: logger.debug(
        "Event: {name} | sender={sender} | keys={keys}",
        name=event.name,
        sender=event.sender,
        keys=list(event.payload.keys()),
    ),
    fail_loud=True,  # PARAM: check after test
)
