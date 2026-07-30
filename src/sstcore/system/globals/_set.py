from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from sstcore import ConfigManager, EventBus, System

_system: System | None = None
_bus: EventBus | None = None
_config: ConfigManager | None = None


def set_all_globals(
    system: System | None, config: ConfigManager | None, bus: EventBus | None
):
    set_global_system(system)
    set_global_config(config)
    set_global_bus(bus)


# IDEA: function like set_global(...) that provides all functionalities
# - *system(),*config() and *bus() just calling them?


def set_global_system(system: System | None) -> None:
    """Register local System as new System or replace former"""

    global _system
    if _system is not None:
        logger.warning(f"Replacing existing global _system: {_system!r}")

    _system = system

    if _system is None:
        logger.info("Global system set to 'None'")
    else:
        logger.info(f"New system set as global: {_system!r}")


def set_global_config(config: ConfigManager | None) -> None:
    """Register local System as new System or replace former"""

    global _config
    if _config is not None:
        logger.warning(f"Replacing existing global _config: {_config!r}")
    _config = config

    if _config is None:
        logger.info("Global config set to 'None'")
    else:
        logger.info(f"New config set as global: {_config!r}")


def set_global_bus(bus: EventBus | None) -> None:
    """Register local EventBus as new EventBus or replace former"""
    global _bus
    if _bus is not None:
        logger.warning(f"Replacing existing global _bus: {_bus!r}")

    _bus = bus

    if _bus is None:
        logger.info("Global bus set to 'None'")
    else:
        logger.info(f"New bus set as global: {_bus!r}")
