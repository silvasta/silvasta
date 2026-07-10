"""
Wire the Event Infrastructure.

Provide decoupled EventBus and MODERN BOOTSTRAP MECHANICS.
"""  # TODO:

# TASK: export strategy
__all__: list[str] = [
    "Event",
    "EventHandler",
    "EventBus",
    "sst_bus",
    "BusRegistrationFunc",
]

from .bus import Event, EventBus, EventHandler
from .loader import sst_bus
from .register import BusRegistrationFunc
