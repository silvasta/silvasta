"""
CliFactory - Experiment 1

- Static meta toolkit and missing args/kwargs

"""

__all__: list[str] = [
    "DtoFactory",
    "dto_factory",
]

from typing import Any, reveal_type

from ....brick.color.box import Colors
from ....port.event.dto import EventDTO, EventDtoFactory
from ....port.link import portlink
from ._produce import (
    CliDtoProducer,
    LineDtoProducer,
    LogDtoProducer,
    MarkdownDtoProducer,
    PanelDtoProducer,
    TableDtoProducer,
)

colors = Colors()

REGISTRY: dict[str, type[Any]] = EventDTO._registry

cli = CliDtoProducer(REGISTRY)

# AI_TASK: how to improve this factory a little bit?
# - the signatures in the EventDtoFactory needs probably to be changed,
#   currently they reflect too much the need of the data structure
# - The goal is to make this a comfortable, user friendly interface
# - The Stubwriter is not already ready for the Stackingcore,
#   still, some first ideas how to mount this would be nice.
# -> check brick.call.stack and come up with ideas how to wire this
# - for the status here, maybe some @property that return the Producer?
# -> suggest some quick improvement for the setup here


@portlink(EventDtoFactory)
class DtoFactory:
    def __init__(self, registry: dict[str, Any]):
        self._registry: dict[str, Any] = registry
        self.log: LogDtoProducer = LogDtoProducer(registry)
        self.cli = CliDtoProducer(registry)
        self.panel = PanelDtoProducer(registry)
        self.md = MarkdownDtoProducer(registry)
        self.line = LineDtoProducer(registry)
        self.table = TableDtoProducer(registry)


dto_factory = DtoFactory(EventDTO._registry)

log_dto = dto_factory.log("My first log message")
cli_dto = dto_factory.cli()

reveal_type(dto_factory.table())
reveal_type(dto_factory.table.from_cols(cols={}))
