"""
Wire the Event Infrastructure.

- Provide EventBus with loader, handler and global access if needed

"""  # TODO: adapt, move to Bus

__all__: list[str] = [
    "System",
    "EventBus",
    "EventHandler",
    "Event",
    "BusRegistrationFunc",
    "sst_bus",
]


from .core import System
from .event_bus import Event, EventBus, EventHandler
from .register import BusRegistrationFunc
from .setup import sst_bus
