"""
Create Global Factory that produces all EventDTOs

- Specialize Functors for EventDTO assemble
  - Update EventDTO.registry if needed
- Mount them reliably with DescriporFields

"""

__all__: list[str] = [
    "dto_factory",
    "DtoFactory",
    # functors
    "LogDtoProducer",
    "CliDtoProducer",
    "PanelDtoProducer",
    "MarkdownDtoProducer",
    "LineDtoProducer",
    "TableDtoProducer",
    # updated dtos
    "TableViewDTO",
]

from ....brick.field import FunctorField as _FunctorField
from ....port.event import dto as _dto
from ....port.event.factory import EventDtoFactory as _EventDtoFactory
from ....port.link import portlink as _portlink
from ._produce import (
    CliDtoProducer,
    LineDtoProducer,
    LogDtoProducer,
    MarkdownDtoProducer,
    PanelDtoProducer,
    TableDtoProducer,
)
from ._table import TableViewDTO  # ensure module loaded


@_portlink(_EventDtoFactory)
class DtoFactory:
    """Mount all DTO Producer"""

    log = _FunctorField(LogDtoProducer)
    cli = _FunctorField(CliDtoProducer)
    panel = _FunctorField(PanelDtoProducer)
    # AI: the below special panels are undesired on this factory
    # box = FunctorField(BoxDtoProducer)
    # header = FunctorField(HeaderDtoProducer)
    md = _FunctorField(MarkdownDtoProducer)
    line = _FunctorField(LineDtoProducer)
    table = _FunctorField(TableDtoProducer)

    def __init__(self, registry: _dto.DtoTable[_dto.EventDTO]) -> None:
        """Reference to the BaseEventDTO subclass registry"""
        self._registry: _dto.DtoTable[_dto.EventDTO] = registry


dto_factory = DtoFactory(_dto.EventDTO._registry)  # LATER: wire into System
