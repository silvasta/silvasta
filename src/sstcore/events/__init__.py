"""
Wire the Event Infrastructure.

- Provide EventBus with loader, handler and global access if needed

"""

__all__: list[str] = [
    "Event",
    "EventHandler",
    "EventBus",
    "sst_bus",
    "BusRegistrationFunc",
]

# TASK: export strategy
# - DTO? protocol?
# - view?

from .bus import Event, EventBus, EventHandler
from .register import BusRegistrationFunc
from .setup import sst_bus
