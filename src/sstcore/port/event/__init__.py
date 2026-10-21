"""
Define the Structure of the Event Data and Pipeline

- Event: The Definition
- EventHandling:
- EventName: Base to derive for Event naming

                                    DependencyLevel.sstcore.port[7]
                                                         color=6+1
"""

__all__: list[str] = [
    "Event",
    "EventHandling",
    "EventBus",
    "BusRegistration",
    #
    "EventDtoFactory",
]


from ._core import BusRegistration, Event, EventBus, EventHandling
from ._fabric import EventDtoFactory
