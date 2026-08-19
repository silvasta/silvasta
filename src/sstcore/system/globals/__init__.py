"""
Set and fetch Global Instances - wireless setup

- System
- ConfigManager
- EventBus

WARN:
- the wired setup is much safer and predictable
- use this for small projects and scripts
                                                       DependencyLevel[4]
"""

from typing import Any

from sstcore.port.functional import python_is_latest

__all__: list[str] = [
    # Fetch
    "system",
    "config",
    "bus",
    # Load
    "load_global_system",
    "load_global_config",
    "load_global_bus",
    "load_all_globals",
    # Set
    "set_global_system",
    "set_global_config",
    "set_global_bus",
    # Reset
    "reset_global_system",
    "reset_global_config",
    "reset_global_bus",
    "reset_all_globals",
    # Change
    "change_all_globals",
]

from ...config import ConfigManager
from .._core import System
from ..event import EventBus
from ._state import _GlobalState

### -- - -- Fetch -- - -- ###


def system() -> System:
    """Fetch Global System Singleton"""
    return _GlobalState.SYSTEM.fetch


def config() -> ConfigManager:
    """Fetch Global ConfigManager Singleton"""
    return _GlobalState.CONFIG.fetch


def bus() -> EventBus:
    """Fetch Global EventBus Singleton"""
    return _GlobalState.BUS.fetch


### -- - -- LOAD -- - -- ###


def load_global_system(override=False) -> None:
    """Load the global System using its default loader"""
    _GlobalState.SYSTEM.load(override)


def load_global_config(override=False) -> None:
    """Load the global ConfigManager using its default loader"""
    _GlobalState.CONFIG.load(override)


def load_global_bus(override=False) -> None:
    """Load the global EventBus using its default loader"""
    _GlobalState.BUS.load(override)


def load_all_globals(override=False):
    """Load all global instances using their default loaders"""
    _GlobalState.load_all(override)


### -- - -- RESET -- - -- ###


def reset_global_system() -> None:
    """Clear the currently set global System instance"""
    _GlobalState.SYSTEM.reset()


def reset_global_config() -> None:
    """Clear the currently set global ConfigManager instance"""
    _GlobalState.CONFIG.reset()


def reset_global_bus() -> None:
    """Clear the currently set global EventBus instance"""
    _GlobalState.BUS.reset()


def reset_all_globals():
    """Clear all currently set global instances"""
    _GlobalState.reset_all()


### -- - -- SET -- - -- ###


def set_global_system(system: System) -> None:
    """Set or replace the global System instance"""
    _GlobalState.SYSTEM.update(instance=system)


def set_global_config(config: ConfigManager) -> None:
    """Set or replace the global ConfigManager instance"""
    _GlobalState.CONFIG.update(instance=config)


def set_global_bus(bus: EventBus) -> None:
    """Set or replace the global EventBus instance"""
    _GlobalState.BUS.update(instance=bus)


### -- - -- CHANGE -- - -- ###

IGNORE = object()


def change_all_globals(
    *,
    system: System | None | Any = IGNORE,
    config: ConfigManager | None | Any = IGNORE,
    bus: EventBus | None | Any = IGNORE,
) -> None:
    """Set multiple or all globals, None for reset, unset values are ignored"""

    if system is not IGNORE:
        _GlobalState.SYSTEM.change(value=system)

    if config is not IGNORE:
        _GlobalState.CONFIG.change(value=config)

    if bus is not IGNORE:
        _GlobalState.BUS.change(value=bus)
