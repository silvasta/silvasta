"""
CliFactory - Experiment 1

- Static meta toolkit and missing args/kwargs

"""

__all__: list[str] = [
    # "CliDtoFactory",
]

from typing import Any

from ....brick.color.box import Colors
from ....brick.reflect import clsname
from ....forge.engine import StaticFuncMeta, StaticFuncMetaData
from ....port.color import ColorBox
from ....port.event.dto import EventDTO, EventDtoFactory, TableDTO
from ....port.link import portlink
from . import _produce

colors: ColorBox = Colors()

REGISTRY: dict[str, type[EventDTO]] = EventDTO._registry


@portlink(EventDtoFactory)
class InitDtoFactory:  # MOVE: to forge.view?
    def __init__(self, registry: dict[str, Any]):
        self._registry: dict[str, Any] = registry

    @property
    def table(self) -> type[TableDTO]:
        return self._registry["table"]


CliDtoFactoryMetaInput = StaticFuncMetaData(
    name=lambda cls: f"󰕧 {clsname(cls)} 󰕧",
    rich=f"{colors.azure('CliDto')}{colors.teal('Factory')}",
    # TODO: attach CliDTO, I mean this is the CliFactory...
    cli="Standard factory for constructing normalized CliDTO renderables",
    color=4,
)
dto_factory = InitDtoFactory(REGISTRY)
dto: TableDTO = dto_factory.table("Render statistic", matrix=[])


@portlink(EventDtoFactory)
class StaticDtoFactory(metaclass=StaticFuncMeta, data=CliDtoFactoryMetaInput):
    """Toolkit for constructing normalized CliDTO items."""

    Table = _produce.table_from_matrix


table: TableDTO = StaticDtoFactory.Table(matrix=[])
