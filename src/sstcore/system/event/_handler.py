"""
Provide Infrastructure for Events

- EventHandler: Process Event with optional Error handling

                                                       DependencyLevel[0]
"""
# NEXT: look at bottom

from typing import Unpack

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

from ...brick.field import StrategyField
from ...forge.func import SafeFunctor
from ...forge.func._safe import SafeFunctorInput
from ...port.event import Event, EventBus, EventHandling
from ...port.functorial import ErrorPolicy
from ...port.link import portlink
from ...util.log import handle_log_event
from ...util.print import printer


def register_default_event_handler(bus: EventBus) -> None:
    # TASK: Replace by Registry - EventRegistry including Wildcard!
    """Attach EventHandler to EventBus by EventName or EventPattern"""

    bus.subscribe("*", CLI_HANDLER)  # payload has cli=...
    bus.subscribe("*", LOG_HANDLER)  # payload has log=...

    bus.subscribe_all(TELEMETRY_HANDLER)


@portlink(EventHandling)
@dataclass(frozen=True)
class EventHandler:
    # TASK: replace by Functor
    """Process Events emitted from the bus in observable Environment"""

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


# MOVE: util.print?
def handle_cli_event(event: Event) -> None:
    # TODO: hand in printer from bootstrap
    """Bridge __cli__ events from the EventBus to the Printer"""

    if cli_payload := event.payload.get("cli"):
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


# MOVE: util.log?
def telemetry(event: Event):
    logger.debug(  # WARN: is this to JSON???
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


@portlink(EventHandling)
class NewEventHandler(SafeFunctor[[Event], None]):
    # LATER: check ErrorHandler.from_func
    """Process Events emitted from the bus in an observable environment."""

    def __init__(self, fail_loud=False, **kwargs: Unpack[SafeFunctorInput]):
        kwargs.setdefault(
            "policy",
            ErrorPolicy.RE_RAISE if fail_loud else ErrorPolicy.LOG_AND_CONTINUE,
        )
        super().__init__(**kwargs)

    @StrategyField
    def _catch(self, error: Exception, /, event: Event) -> None:
        if self.policy == ErrorPolicy.RE_RAISE:
            raise RuntimeError(f"Critical Fail: {self}") from error

        logger.error(f"{self} failed for '{event.name}': {error}")
        logger.debug(f"Traceback for {self}:", exc_info=True)


NEW_LOG_HANDLER = NewEventHandler(
    name="LoguruBridge",
    call=handle_log_event,
    fail_loud=True,
)
