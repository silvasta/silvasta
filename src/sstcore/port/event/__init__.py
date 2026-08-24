"""
Define the Structure of the Event Data and Pipeline

- Event: The Definition
- EventHandler:
- EventName: Base to derive for Event naming

- LogDTO  Intended for __log__ and processed by logger
- CliDTO: Intended for __cli__ and processed by printer

"""

__all__: list[str] = [
    "Event",
    "EventHandler",
    "EventBus",
    "BusRegistration",
]


from ._core import BusRegistration, Event, EventBus, EventHandler
