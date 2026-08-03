"""
Wire the Event Infrastructure.

- Provide EventBus with Loader, Handler and if needed, global access
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "EventBus",
    "EventHandler",
    #
    "Emitter",
    "EmitFunctor",
]


from ._bus import EventBus, EventHandler
from ._emit import EmitFunctor, Emitter
