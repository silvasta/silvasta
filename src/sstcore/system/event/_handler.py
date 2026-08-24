"""
Provide Infrastructure for Events

- EventBus: Route Events by name to registred EventHandler
- EventHandler: Process Event with optional Error handling
                                                       DependencyLevel[0]
"""

from typing import TYPE_CHECKING, Any

__all__: list[str] = [
    "EventHandler",
    # presets
    "register_default_event_handler",
    "LOG_HANDLER",
    "CLI_HANDLER",
    "TELEMETRY_HANDLER",
    "telemetry",
]

from collections.abc import Callable
from dataclasses import dataclass

from loguru import logger

from ...port.event import Event, EventBus
from ...port.event import EventHandler as EventHandler_
from ...util import printer
from ...util.log import handle_log_event


def register_default_event_handler(bus: EventBus) -> None:
    # REMOVE: replace by Register
    """Attach EventHandler to EventBus by EventName or EventPattern"""

    bus.subscribe("*", CLI_HANDLER)  # payload has cli=...
    bus.subscribe("*", LOG_HANDLER)  # payload has log=...

    bus.subscribe_all(TELEMETRY_HANDLER)


@dataclass(frozen=True)
class EventHandler:
    """Process Events emmited from the bus in observable Environment"""

    name: str
    func: Callable[[Event], None]
    fail_loud: bool = False

    def __str__(self) -> str:
        return f"EventHandler[{self.name}]"

    def __call__(self, event: Event) -> None:
        """Execute handler function and manage fail if flag is set"""
        try:
            self.func(event)
        except Exception as error:
            if self.fail_loud:  # LATER: custom error?
                raise RuntimeError(f"Critical Fail: {self}") from error

            logger.error(f"{self} failed for '{event.name}': {error}")
            logger.debug(f"Traceback for {self}:", exc_info=True)


def handle_cli_event(event: Event) -> None:
    """Bridge __cli__ events from the EventBus to the Printer"""
    # TODO: hand in printer from bootstrap
    cli_payload: Any | None = event.payload.get("cli")
    if cli_payload is None:
        return
    printer(cli_payload)


# REMOVE: replace by Functor
LOG_HANDLER = EventHandler(
    name="LoguruBridge",
    func=handle_log_event,
    fail_loud=True,
)

# REMOVE: replace by Functor
CLI_HANDLER = EventHandler(
    name="CliPrinter",
    func=handle_cli_event,
    fail_loud=True,
)


# MOVE: util.log
def telemetry(event: Event):
    logger.debug(
        "Event: {event_name} | sender={sender} | keys={keys}",
        event_name=event.name,
        sender=event.sender,
        keys=list(event.payload.keys()),
    )


# REMOVE: replace by Functor
TELEMETRY_HANDLER = EventHandler(
    name="Telemetry",
    func=telemetry,
    fail_loud=False,
)

if TYPE_CHECKING:
    _instance_check: EventHandler_ = EventHandler("dummy", lambda _e: None)
    _class_check: type[EventHandler_] = EventHandler
