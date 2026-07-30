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
    "register_default_event_handler",
]


from ._bus import EventBus, EventHandler
from ._emit import EmitFunctor, Emitter
from ._register import BusRegistrationFunc, register_default_event_handler
