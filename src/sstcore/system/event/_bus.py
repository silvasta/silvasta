"""
Provide Infrastructure for Events

- EventBus: Route Events by name to registered EventHandling

                            DependencyLevel.sstcore.system.event[2]
"""

__all__: list[str] = [
    "Bus",
]

from typing import Self, Unpack

from ...brick.reflect import clsname
from ...port.event import Event, EventBus, EventHandling
from ...port.event.name import CoreEvent, EventName, EventPattern
from ...port.link import portlink
from ...port.system import BusInput, BusSpec
from ._handler import DEFAULT_HANDLERS, EventHandler
from ._registry import BusRegistry


@portlink(EventBus)
class Bus:
    def __init__(self, registry: BusRegistry | None = None) -> None:
        self.registry: BusRegistry = (
            registry if registry is not None else BusRegistry()
        )

    def emit(self, event: EventName, /, sender: str, **payload) -> None:
        """Root of all Emits"""

        core_event = Event(name=event, sender=sender, payload=payload)

        for handler in self.registry.find(core_event):
            handler(core_event)

    def subscribe(
        self, handler: EventHandling, pattern: EventPattern | None = None
    ) -> None:
        if isinstance(handler, EventHandler):
            if pattern is not None:
                handler.pattern = pattern
            self.registry.add(handler)
        else:
            if pattern is None:
                raise ValueError("Need Pattern for raw Function!")
            self.registry.add(EventHandler(call=handler, pattern=pattern))

    def subscribe_all(self, handler: EventHandling) -> None:
        self.subscribe(handler, pattern="*")

    @property
    def n_global_handler(self) -> int:
        return self.registry.count("*")

    @property
    def n_handler(self) -> int:
        return len(self.registry) - self.n_global_handler

    def __str__(self) -> str:
        return clsname(self)

    def __repr__(self) -> str:
        return f"{self}(  {self.n_global_handler} 󰌌 {self.n_handler} 󰍹 )"

    @classmethod
    def ready(cls, **kwargs: Unpack[BusInput]) -> Self:
        bus: Self = cls()
        spec = BusSpec(**kwargs)

        if spec.use_default_registration:
            bus.registry.add(list(DEFAULT_HANDLERS))

        if spec.bus_registration:  # LATER: just inject prepared registry?
            spec.bus_registration(bus)

        bus.emit(
            CoreEvent.BUS_READY,
            sender=f"{bus}",
            log="EventBus setup complete",
        )
        return bus
