"""
Wire the Event Infrastructure

- Provide EventBus with Bootstrap and Handler access

"""

__all__: list[str] = [
    "Bus",
    "EventHandler",
    #
    "EmitCore",
    "LogEmitter",  # FIX:
    "CliEmitter",  # FIX:
]


from ._bus import Bus, EventHandler
from ._emit import EmitCore, LogEmitter
