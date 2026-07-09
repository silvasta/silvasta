"""
Wire the Event Infrastructure.

Prepare default EventBus subscriprions and assemble the current EventSystem

- sstbus: preconfigure global Singleton

- EventSystem: container for bus, and...
  - NOTE: preview for future box with config, printer, bus, ...

"""  # TODO: synchronize with config description text (and setup?)

from collections.abc import Callable
from typing import Any, Self

from loguru import logger

from ..config import ConfigManager
from ..utils import Printer, printer
from ..utils.log.event_handler import handle_log_event
from ..utils.print.event_handler import handle_cli_event
from .bus import BusRegistrationFunc, EventBus, EventHandler

log_handler = EventHandler(
    name="LoguruBridge",
    func=handle_log_event,
    fail_loud=True,  # PARAM: log_handler: check after test
)
cli_handler = EventHandler(
    name="CliPrinter",
    func=handle_cli_event,
    fail_loud=True,  # PARAM: log_handler: check after test
)

TELEMETRY_LOUD = True  # PARAM: set False after tests


def register_default_event_handler(bus: EventBus) -> None:
    """Attach EventHandler to EventBus registry by event_name"""

    for name in ("sys.log", "sys.error", "sys.warn"):
        bus.subscribe(name, log_handler)

    # LATER: develeop system for event_names and handler

    for name in ("ui.panel", "ui.table", "ui.line", "ui.markdown"):
        bus.subscribe(name, cli_handler)

    def telemetry(event: Any) -> None:
        logger.debug(
            "Event: {name} | sender={sender} | payload_keys={keys}",
            name=event.name,
            sender=event.sender,
            keys=list(event.payload.keys()),
        )

    bus.subscribe_all(EventHandler("telemetry", telemetry, TELEMETRY_LOUD))


type SystemLoader = (  # TODO: finalize
    Callable[[ConfigManager | None, Printer | None], EventSystem]
    | Callable[[], EventSystem]
)


def build_event_system() -> EventSystem:
    """Simple entrypoint for scripts/small projects."""
    # AI: something like this as default SystemLoader?
    return EventSystem.build()


class EventSystem:
    """Hold the EventBus and related components"""

    def __init__(self, bus: EventBus, printer: Printer):
        self.bus: EventBus = bus
        self.printer: Printer = printer
        # AI: attach config here? setup log?

    # AI_TASK: decorator for attach, here and|or EventBus

    @classmethod
    def build(
        cls,
        config: ConfigManager | None = None,
        custom_printer: Printer | None = None,
        use_default_handler: bool = True,
        attach: BusRegistrationFunc | None = None,
    ) -> Self:
        """Assemble the EventBus and other components to the EventSystem"""

        system_printer: Printer = custom_printer or printer

        if config:
            system_printer.project_name = config.project_name
            system_printer.project_version = config.project_version
            # LATER: register_project_handlers(bus, config)

        bus = EventBus()

        if use_default_handler:
            register_default_event_handler(bus)

        if attach:  # BusRegistrationFunc
            attach(bus)

        return cls(bus=bus, printer=system_printer)

    def emit(self, event_name: str, sender: str, **payload: Any) -> None:
        """Increase convenience for bus access"""
        self.bus.emit(event_name, sender, **payload)


# STRATEGY: rethink global singleton setup, how and where to apply
# Lazy singleton for tiny projects or scripts
_event_system: EventSystem | None = None


def get_event_system() -> EventSystem:  # TODO: check, compare, finalize
    """
    Provide EventSystem from global Cache and load at first call

    - Intended for small projects and scripts
    """
    global _event_system
    if _event_system is None:
        _event_system = EventSystem.build()
    return _event_system


def sst_bus() -> EventBus:  # TODO: check, compare, finalize
    """Provide default EventBus"""
    return get_event_system().bus
