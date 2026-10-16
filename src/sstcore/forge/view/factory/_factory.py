"""
CliFactory - Experiment 1

- Static meta toolkit and missing args/kwargs

"""

from typing import reveal_type

__all__: list[str] = [
    "DtoFactory",
    "dto_factory",
]


from ....brick.field._functor import (
    FunctorField,
    FunctorField1,
    FunctorField2,
    FunctorField3,
)
from ....port.event import _fabric
from ....port.event.dto import DtoTable, EventDTO
from ....port.link import portlink
from . import _produce
from ._produce import (
    CliDtoProducer,
    LineDtoProducer,
    LogDtoProducer,
    MarkdownDtoProducer,
    PanelDtoProducer,
    TableDtoProducer,
)


@portlink(_fabric.EventDtoFactory1)
@portlink(_fabric.EventDtoFactory2)
@portlink(_fabric.EventDtoFactory3)
class Factory:
    # AI: this is how the Fields should look!
    log = FunctorField(_produce.LogDtoProducer)
    cli = FunctorField(_produce.CliDtoProducer)
    panel = FunctorField(_produce.PanelDtoProducer)
    md = FunctorField(_produce.MarkdownDtoProducer)
    line = FunctorField(_produce.LineDtoProducer)
    table = FunctorField(_produce.TableDtoProducer)

    def __init__(self, registry: DtoTable[EventDTO]) -> None:
        self._registry: DtoTable[EventDTO] = registry


factory = Factory(EventDTO._registry)

reveal_type(factory.log.__call__)
reveal_type(factory.cli.__call__)
reveal_type(factory.panel.__call__)
reveal_type(factory.table.__call__)
factory.table.from_cols({})


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@portlink(_fabric.EventDtoFactory1)
@portlink(_fabric.EventDtoFactory2)
@portlink(_fabric.EventDtoFactory3)
class Factory3:
    # AI: this is how the Fields should look!
    log = FunctorField3(_produce.LogDtoProducer)
    cli = FunctorField3(_produce.CliDtoProducer)
    panel = FunctorField3(_produce.PanelDtoProducer)
    md = FunctorField3(_produce.MarkdownDtoProducer)
    line = FunctorField3(_produce.LineDtoProducer)
    table = FunctorField3(_produce.TableDtoProducer)

    def __init__(self, registry: DtoTable[EventDTO]) -> None:
        self._registry: DtoTable[EventDTO] = registry


factory3 = Factory3(EventDTO._registry)

reveal_type(factory3.log.__call__)
reveal_type(factory3.cli.__call__)
reveal_type(factory3.panel.__call__)
reveal_type(factory3.table.__call__)
factory3.table.from_cols({})

#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@portlink(_fabric.EventDtoFactory1)
@portlink(_fabric.EventDtoFactory2)
@portlink(_fabric.EventDtoFactory3)
class Factory2:
    # AI: stringly typed repetitions are not desired
    log = FunctorField2(_produce.LogDtoProducer, "_registry")
    cli = FunctorField2(_produce.CliDtoProducer, "_registry")
    panel = FunctorField2(_produce.PanelDtoProducer, "_registry")
    md = FunctorField2(_produce.MarkdownDtoProducer, "_registry")
    line = FunctorField2(_produce.LineDtoProducer, "_registry")
    table = FunctorField2(_produce.TableDtoProducer, "_registry")

    def __init__(self, registry: DtoTable[EventDTO]) -> None:
        self._registry: DtoTable[EventDTO] = registry


factory2 = Factory2(EventDTO._registry)

reveal_type(factory2.log("*"))
reveal_type(factory2.cli(""))
factory2.table()
factory2.table.from_cols({})


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def loader(unit) -> LogDtoProducer:
    return LogDtoProducer(unit._registry)


# @portlink(_fabric.EventDtoFactory1)
# @portlink(_fabric.EventDtoFactory2)
# @portlink(_fabric.EventDtoFactory3)
class Factory1:
    log = FunctorField1(LogDtoProducer, loader=loader)
    # cli = FunctorField1(CliDtoProducer, "_registry")
    cli = FunctorField1(
        CliDtoProducer, loader=lambda s: CliDtoProducer(s._registry)
    )
    panel = FunctorField1(PanelDtoProducer, "_registry")
    md = FunctorField1(MarkdownDtoProducer, "_registry")
    line = FunctorField1(LineDtoProducer, "_registry")
    table = FunctorField1(TableDtoProducer, "_registry")


factory1 = Factory1()

reveal_type(factory1.log("*"))
reveal_type(factory1.cli(""))
factory1.table()
factory1.table.from_cols({})


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@portlink(_fabric.EventDtoFactory1)
@portlink(_fabric.EventDtoFactory2)
@portlink(_fabric.EventDtoFactory3)
class DtoFactory:
    def __init__(self, registry: DtoTable):
        self._registry: DtoTable = registry
        self.log = _produce.LogDtoProducer(registry)
        self.cli = _produce.CliDtoProducer(registry)
        self.panel = _produce.PanelDtoProducer(registry)
        self.md = _produce.MarkdownDtoProducer(registry)
        self.line = _produce.LineDtoProducer(registry)
        self.table = _produce.TableDtoProducer(registry)


dto_factory = DtoFactory(EventDTO._registry)  # LATER: distribute by System?
