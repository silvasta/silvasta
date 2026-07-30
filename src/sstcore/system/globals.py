"""
Central Registry for sstcore Singletons.

- Set and fetch global instances of System, ConfigManager, and EventBus.
"""

__all__: list[str] = [
    "remove_all_globals",
    "set_global_system",
    "set_global_config",
    "set_global_bus",
    "set_all_globals",
    "system",
    "config",
    "bus",
]

from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from sstcore import ConfigManager, EventBus, System


class _GlobalState:
    system: System | None = None
    config: ConfigManager | None = None
    bus: EventBus | None = None


_STATE = _GlobalState()


def remove_all_globals() -> None:
    set_all_globals(system=None, config=None, bus=None)


def set_global_system(system: System | None) -> None:
    _update_state("system", system)


def set_global_config(config: ConfigManager | None) -> None:
    _update_state("config", config)


def set_global_bus(bus: EventBus | None) -> None:
    _update_state("bus", bus)


def system() -> System:
    # LATER: property of _GlobalState?
    """Fetch Global System Singleton"""
    if _STATE.system is None:
        raise RuntimeError("No access to global system without bootstrap!")
    logger.debug("provide cached system")
    return _STATE.system


def config() -> ConfigManager:
    # LATER: property of _GlobalState?
    """Fetch Global ConfigManager Singleton"""
    if _STATE.config is None:
        raise RuntimeError("No access to global config without bootstrap!")
    logger.debug("provide cached config")
    return _STATE.config


def bus() -> EventBus:
    # LATER: property of _GlobalState?
    """Fetch Global EventBus Singleton"""
    if _STATE.bus is None:
        raise RuntimeError("No access to global bus without bootstrap!")
    logger.debug("provide cached bus")
    return _STATE.bus


def _update_state(name: str, instance: Any) -> None:
    # LATER: function of _GlobalState?
    """Generic logic for updating state and logging."""
    current = getattr(_STATE, name)

    if current is not None and instance is not None:
        logger.warning(f"Replacing existing global {name}: {current!r}")

    setattr(_STATE, name, instance)

    if instance is None:
        logger.info(f"Global {name} set to 'None'")
    else:
        logger.info(f"New {name} set as global: {instance!r}")


def set_all_globals(
    *,
    system: System | None = None,
    config: ConfigManager | None = None,
    bus: EventBus | None = None,
) -> None:
    set_global_system(system)
    set_global_config(config)
    set_global_bus(bus)
