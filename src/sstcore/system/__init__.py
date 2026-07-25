"""
Wire the Event Infrastructure.

- Provide EventBus with loader, handler and if needed, global access

"""  # TODO: adapt, move to Bus

__all__: list[str] = [
    "System",
    "EventBus",
    "EventHandler",
    "BusRegistrationFunc",
    "sst_bus",
    "EmitFunctor",
    "Emitter",
]


from .bus import EventBus, EventHandler
from .core import System
from .emit import EmitFunctor, Emitter
from .register import BusRegistrationFunc
from .setup import sst_bus
