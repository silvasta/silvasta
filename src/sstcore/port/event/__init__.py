"""
Define the Structure of the Event Data and Pipeline

- Event: The Definition
- EventHandler:
- EventName: Base to derive for Event naming

                                    DependencyLevel.sstcore.port[7]
                                                         color=6+1
"""

__all__: list[str] = [
    "Event",
    "EventHandler",
    "EventBus",
    "BusRegistration",
]


from ._core import BusRegistration, Event, EventBus, EventHandler
