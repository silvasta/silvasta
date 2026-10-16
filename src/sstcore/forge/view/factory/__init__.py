"""
Prepare for any EventDTO

- Assemble the Producer and Factory

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

from ._factory import DtoFactory, dto_factory
from ._produce import (
    CliDtoProducer,
    LineDtoProducer,
    LogDtoProducer,
    MarkdownDtoProducer,
    PanelDtoProducer,
    TableDtoProducer,
)
from ._table import TableViewDTO  # ensure module loaded
