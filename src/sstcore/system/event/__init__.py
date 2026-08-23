"""
Wire the Event Infrastructure

- Provide EventBus with Bootstrap and Handler access

"""

__all__: list[str] = [
    "EventBus",
    "EventHandler",
    #
    "Emitter",
    "LogEmitter",  # FIX:
    "CliEmitter",  # FIX:
]


from ._bus import EventBus, EventHandler
from ._emit import Emitter
