"""
Define the Shape and Structure of Functions and Classes.

- Event: The Definition
- EventName: Base to derive for Event naming
- EmitFunc: Skeleton for exporting bus.emit functions

- LogDTO  Intended for __log__ and processed by logger
- CliDTO: Intended for __cli__ and processed by printer

"""

__all__: list[str] = [
    "Event",
    "EventHandler",
    "EventBus",
    "BusRegistration",
    #
    "EventName",
    #
    "Emit",
    "EventEmit",
    "LogEmit",
    "LogEmitter",
    "ViewEmitter",
    "Emitter",
    #
    "LogDTO",
    "CliDTO",
]


from ._core import BusRegistration, Event, EventBus, EventHandler
from ._emit import Emit, Emitter
from .dto import CliDTO, LogDTO
from .name import EventName
