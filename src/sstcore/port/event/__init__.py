"""
Define the Structure of the Event Data and Pipeline

- Event: The Definition
- EventHandler:
- EventName: Base to derive for Event naming

- CliDTO: CliRenderable snapshot with __cli__ to Printer
- LogDTO: LogSerializable message with __log__ to Loguru

                                                 DependencyLevel[4]
                                                         calling[2]
                                                           color[3]
"""

__all__: list[str] = [
    "Event",
    "EventHandler",
    "EventBus",
    "BusRegistration",
    # dto and view
    "CliRenderable",
    "CliDTO",
    "LogSerializable",
    "LogDTO",
]


from ._core import BusRegistration, Event, EventBus, EventHandler
from .dto import CliDTO, CliRenderable, LogDTO, LogSerializable
