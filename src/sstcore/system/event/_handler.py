"""
Provide Infrastructure for Events

- EventHandler: Process Event with optional Error handling

                            DependencyLevel.sstcore.system.event[0]
"""

from typing import Self, Unpack

__all__: list[str] = [
    "EventHandler",
    # presets
    "LOG_HANDLER",
    "CLI_HANDLER",
    "TELEMETRY_HANDLER",
    "DEFAULT_HANDLERS",
]

import fnmatch
from collections.abc import Callable

from loguru import logger

from ...brick.field import StrategyField
from ...brick.reflect import funcname
from ...forge.func import SafeFunctor
from ...forge.func._safe import SafeFunctorInput
from ...port.event import Event, EventHandling
from ...port.event.name import EventPattern
from ...port.functorial import ErrorPolicy
from ...port.link import portlink
from ...util.log import handle_log_event
from ...util.print import printer


@portlink(EventHandling)
class EventHandler(SafeFunctor[[Event], None]):
    """Process Events emitted from the bus in an observable environment."""

    def __init__(
        self,
        pattern: EventPattern = "*",
        *,
        fail_loud=False,
        **kwargs: Unpack[SafeFunctorInput[[Event], None]],
    ):
        self.pattern: EventPattern = pattern
        kwargs.setdefault(
            "policy",
            ErrorPolicy.RE_RAISE if fail_loud else ErrorPolicy.LOG_AND_CONTINUE,
        )
        super().__init__(**kwargs)

    def _format_name(self, name: str = "") -> str:
        """Format str:= [(Cls)][{name}::{pattern}]"""
        return f"{name or super()._format_name()}::{self.pattern}"

    def handles(self, event: Event | EventPattern) -> bool:
        """Does the Handler match the Event?"""
        target: str = event.name if isinstance(event, Event) else event
        return self.pattern == "*" or fnmatch.fnmatch(target, self.pattern)

    @StrategyField
    def _catch(self, error: Exception, /, event: Event) -> None:
        if self.policy == ErrorPolicy.RE_RAISE:
            raise RuntimeError(f"Critical Fail: {self}") from error

        logger.error(f"{self} failed for '{event.name}': {error}")
        logger.debug(f"Traceback for {self}:", exc_info=True)

    @classmethod
    def from_func(  # CHECK: benefit over EventHandler(...)? @decorator? no...
        cls,
        func: Callable[[Event], None],
        *,
        pattern: EventPattern = "*",
        fail_loud: bool = False,
        name: str = "",
    ) -> Self:
        """Build EventHandler from a plain function."""
        # AI: for ErrorHandler this made much more sense, error_type extraction
        return cls(
            pattern=pattern,
            call=func,
            fail_loud=fail_loud,
            name=name or funcname(func, default="CustomEventHandler"),
        )


def handle_cli_event(event: Event) -> None:  # TODO: printer from..??
    """Bridge __cli__ events from the EventBus to the Printer"""
    if cli_payload := event.payload.get("cli"):
        printer(cli_payload)


def telemetry(event: Event) -> None:  # CHECK: what about ndjson??
    logger.debug(
        "Event: {event_name} | sender={sender} | keys={keys}",
        event_name=event.name,
        sender=event.sender,
        keys=list(event.payload.keys()),
    )


# AI: here below the verion I prefere without decorator when not clearly better
# - can I remove the .from_func?

LOG_HANDLER = EventHandler(  # CHECK: better from_func?
    call=handle_log_event,
    pattern="*",
    name="LoguruBridge",
    fail_loud=True,
)

CLI_HANDLER = EventHandler.from_func(  # CHECK: why from_func?
    handle_cli_event,
    pattern="*",
    name="CliPrinter",
    fail_loud=True,
)


TELEMETRY_HANDLER = EventHandler(
    call=telemetry,
    pattern="*",
    name="Telemetry",
    fail_loud=False,
)

DEFAULT_HANDLERS: tuple[EventHandler, ...] = (
    TELEMETRY_HANDLER,
    CLI_HANDLER,
    LOG_HANDLER,
)
