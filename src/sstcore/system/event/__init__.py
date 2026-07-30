"""
Wire the Event Infrastructure.

- Provide EventBus with Loader, Handler and if needed, global access
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "Emitter",
    "EmitFunctor",
    "EventBus",
    "EventHandler",
    "BusRegistrationFunc",
    "create_event_bus",
]


from ._bus import EventBus, EventHandler
from ._emit import EmitFunctor, Emitter
from ._register import BusRegistrationFunc
from ._setup import create_event_bus
