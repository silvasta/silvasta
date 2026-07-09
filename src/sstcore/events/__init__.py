"""
Wire the Event Infrastructure.

Provide decoupled EventBus and MODERN BOOTSTRAP MECHANICS.
"""

# TASK: export strategy
__all__: list[str] = [
    "Event",
    "EventHandler",
    "EventBus",
    # "sst_bus",
    # "EventSystem",
]

from .bus import Event, EventBus, EventHandler
# from .core import sst_bus
