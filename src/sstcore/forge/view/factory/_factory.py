"""
CliFactory - Experiment 1

- Static meta toolkit and missing args/kwargs

"""

__all__: list[str] = [
    "DtoFactory",
    "dto_factory",
]


from ....brick.field._functor import FunctorField
from ....port.event import _fabric
from ....port.event.dto import DtoTable, EventDTO
from ....port.link import portlink
from . import _produce


@portlink(_fabric.EventDtoFactory)
class DtoFactory:
    log = FunctorField(_produce.LogDtoProducer)
    cli = FunctorField(_produce.CliDtoProducer)
    panel = FunctorField(_produce.PanelDtoProducer)
    md = FunctorField(_produce.MarkdownDtoProducer)
    line = FunctorField(_produce.LineDtoProducer)
    table = FunctorField(_produce.TableDtoProducer)

    def __init__(self, registry: DtoTable[EventDTO]) -> None:
        self._registry: DtoTable[EventDTO] = registry


dto_factory = DtoFactory(EventDTO._registry)  # LATER: distribute by System?
