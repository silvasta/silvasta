"""Centralized globals for sstcore.

Intended for scripts and small projects.
Larger projects should prefer explicit instances + custom loaders.

                                                       DependencyLevel[X]
"""

__all__: list[str] = [
    "system",
    "config",
    "bus",
    "set_all_globals",
    "remove_all_globals",
    "set_global_system",
    "set_global_config",
    "set_global_bus",
]
from ._set import (
    set_all_globals,
    set_global_bus,
    set_global_config,
    set_global_system,
)


def remove_all_globals():
    set_all_globals(system=None, config=None, bus=None)
