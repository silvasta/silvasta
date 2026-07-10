"""
Hold and prepare Global Singleton EventBus instance.

- Provide protected access to initial setup (unlock with flag)
- Prepare ready-to-use loader for CLI, or any other purpose
- Handle infrastructure for project setups with custom loader
- Expose global Singleton: `bus: EventBus = sst_bus()`

"""

from collections.abc import Callable

from loguru import logger

from .bus import EventBus
from .register import register_default_event_handler

_bus: EventBus | None = None

type BusLoader = Callable[[], EventBus]


def sst_bus(*, _allow_uninitialized: bool = False) -> EventBus:
    """Fetch Global Singleton EventBus instance"""

    global _bus
    if _bus is None:
        logger.warning("Bus accessed before Bootstrap!")

        if _allow_uninitialized:
            logger.warning("Loading Bus with default setup")
            return setup_event_bus()

        raise RuntimeError("No access to bus without bootstrap!")
    logger.debug("provide cached config")

    return _bus


def sst_bus_loader() -> EventBus:
    """Prepare Loader function ready to setup EventBus"""

    return setup_event_bus()


def setup_event_bus():
    """Load EventBus explicit as one-time initialization"""

    global _bus
    if _bus is not None:
        logger.warning("EventBus is already initialized, ignoring override!")
        return _bus

    logger.info("Setup EventBus with default handler...")

    _bus = EventBus()
    register_default_event_handler(_bus)

    logger.info("EventBus setup completed")

    return _bus
