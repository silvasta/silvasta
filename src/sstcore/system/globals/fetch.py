"""Fetch instances from global cache"""

__all__: list[str] = [
    "system",
    "config",
    "bus",
]


from typing import TYPE_CHECKING

from loguru import logger

# from ._set import _system ... # AI_QUESTION: does this make sense?


_system: System | None  # AI_QUESTION: or just use like this?
_bus: EventBus | None
_config: ConfigManager | None

if TYPE_CHECKING:
    from sstcore import ConfigManager, EventBus, System

# IDEA: function like fetch_global(...) that provides all functionalities
# - system(),config() and bus() just calling them?


def system() -> System:
    """Fetch Global System Singleton"""

    global _system
    if _system is None:
        raise RuntimeError("No access to global _system without bootstrap!")
    # TODO: emit?
    logger.debug("provide cached _system")

    return _system


def config() -> ConfigManager:
    """Fetch Global ConfigManager Singleton"""

    global _config
    if _config is None:
        raise RuntimeError("No access to global _config without bootstrap!")
    logger.debug("provide cached _config")

    return _config


def bus() -> EventBus:
    """Fetch Global EventBus Singleton"""

    global _bus
    if _bus is None:
        raise RuntimeError("No access to global _bus without bootstrap!")
    logger.debug("provide cached bus")

    return _bus
