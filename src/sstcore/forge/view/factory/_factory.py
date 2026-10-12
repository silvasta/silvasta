"""
CliFactory - Experiment 1

- Static meta toolkit and missing args/kwargs

"""

__all__: list[str] = [
    "DtoFactory",
    "dto_factory",
]

from typing import Any

from ....brick.color.box import Colors
from ....port.event.dto import EventDTO, EventDtoFactory
from ....port.link import portlink

colors = Colors()

REGISTRY: dict[str, type[EventDTO]] = EventDTO._registry


@portlink(EventDtoFactory)
class DtoFactory:
    def __init__(self, registry: dict[str, Any]):
        self._registry: dict[str, Any] = registry


dto_factory = DtoFactory(EventDTO._registry)
