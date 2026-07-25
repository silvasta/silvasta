"""
Hold and prepare Global Singleton EventBus instance.

- Provide protected access to initial setup (unlock with flag)
- Prepare ready-to-use loader for CLI, or any other purpose
- Handle infrastructure for project setups with custom loader
- Expose global Singleton: `bus: EventBus = sst_bus()`

"""

from sstcore.contract.event import CoreEvent

__all__: list[str] = [
    "BusLoader",
    "sst_bus_loader",
    "sst_bus",
    "create_event_bus",
    "set_global_bus",
]
from collections.abc import Callable

from loguru import logger

from .bus import EventBus
from .register import BusRegistrationFunc, register_default_event_handler

type BusLoader = Callable[..., EventBus]


def sst_bus_loader(
    bus_registration: BusRegistrationFunc | None = None,
    use_default_registration=True,
    #
    use_global=False,
) -> BusLoader:
    """Prepare Loader function ready to setup EventBus"""

    def loader() -> EventBus:
        return create_event_bus(
            bus_registration=bus_registration,
            use_default_registration=use_default_registration,
            use_global=use_global,
        )

    return loader


_bus: EventBus | None = None


def sst_bus() -> EventBus:
    """Fetch Global EventBus Singleton"""

    global _bus
    if _bus is None:
        raise RuntimeError("No access to global _bus without bootstrap!")
    logger.debug("provide cached bus")

    return _bus


def create_event_bus(
    bus_registration: BusRegistrationFunc | None = None,
    use_default_registration=True,
    #
    use_global=False,
) -> EventBus:
    """Load EventBus explicit as one-time initialization"""

    bus = EventBus()

    if use_default_registration:
        register_default_event_handler(bus)

    if bus_registration:
        bus_registration(bus)

    # logger.info("EventBus setup complete")
    bus.emit(
        event_name=CoreEvent.BUS_DIAG,
        sender="BusSetup",
        log="EventBus setup complete",
    )

    if use_global:
        set_global_bus(bus)
    return bus


def set_global_bus(bus: EventBus | None) -> None:
    """Register local EventBus as new EventBus or replace former"""
    # TODO: emit?
    global _bus
    if _bus is not None:
        logger.warning(f"Replacing existing global _bus: {_bus!r}")
        # TODO: emit old And new?

    _bus = bus

    if _bus is None:
        # TODO: emit?
        logger.info("Global bus set to 'None'")
    else:
        # TODO: emit?
        logger.info(f"New bus set as global: {_bus!r}")
