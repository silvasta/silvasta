"""
Central Registry for sstcore Singletons.

- Set and fetch global instances of System, ConfigManager, and EventBus.
"""

__all__: list[str] = [
    "system",
    "config",
    "bus",
    "set_global_system",
    "set_global_config",
    "set_global_bus",
    "set_all_globals",
    "remove_all_globals",
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


def _update_state(name: str, instance: Any) -> None:
    """Generic logic for updating state and logging."""
    current = getattr(_STATE, name)

    if current is not None and instance is not None:
        logger.warning(f"Replacing existing global {name}: {current!r}")

    setattr(_STATE, name, instance)

    if instance is None:
        logger.info(f"Global {name} set to 'None'")
    else:
        logger.info(f"New {name} set as global: {instance!r}")


# 4. Strongly Typed Setters wrapping the generic helper
def set_global_system(system_instance: System | None) -> None:
    _update_state("system", system_instance)


def set_global_config(config_instance: ConfigManager | None) -> None:
    _update_state("config", config_instance)


def set_global_bus(bus_instance: EventBus | None) -> None:
    _update_state("bus", bus_instance)


# 5. Bulk Operations
def set_all_globals(
    system_instance: System | None = None,
    config_instance: ConfigManager | None = None,
    bus_instance: EventBus | None = None,
) -> None:
    set_global_system(system_instance)
    set_global_config(config_instance)
    set_global_bus(bus_instance)


def remove_all_globals() -> None:
    set_all_globals(
        system_instance=None, config_instance=None, bus_instance=None
    )
