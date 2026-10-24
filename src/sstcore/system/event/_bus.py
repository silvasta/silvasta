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

# INFO: start
# class EventHandling(Protocol):
#     def __call__(self, event: Event, /) -> None:
#         """Process emitted Events dispatched by the Bus"""
# class BusInput(TypedDict, total=False):
#     bus_registration: BusRegistration | None
#     use_default_registration: bool
# @dataclass
# class BusSpec:
#     bus_registration: BusRegistration | None = None
#     use_default_registration: bool = True
# class BusRegistration(Protocol):
#     def __call__(self, bus: EventBus) -> None:
#         """Subscribe EventHandling by EventName or Wildcard to EventBus"""
# INFO: end


@portlink(EventBus)
class Bus:
    def __init__(self, registry: BusRegistry | None = None) -> None:
        self.registry: BusRegistry = registry or BusRegistry()

    def emit(self, event: EventName, /, sender: str, **payload) -> None:

        core_event = Event(name=event, sender=sender, payload=payload)

        for handler in self.registry.resolve(event):
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
        return self.registry.count(lambda h: h.pattern == "*")

    @property
    def n_handler(self) -> int:
        return self.registry.count(lambda h: h.pattern != "*")

    def __str__(self) -> str:
        return clsname(self)

    def __repr__(self) -> str:
        return f"{self}(  {self.n_global_handler} 󰌌 {self.n_handler} 󰍹 )"

    # def _match_subscribers(self, event: EventName) -> tuple[EventHandling, ...]:
    #     """Filter subscribers by event name and wildcard pattern"""
    #
    #     subscribers: tuple[EventPattern, ...] = tuple(self._subscribers.keys())
    #
    #     matched_handlers: list[EventHandling] = [
    #         handler
    #         for pattern in _get_patterns(event, subscribers)
    #         for handler in self._subscribers[pattern]
    #     ]
    #
    #     return tuple(dict.fromkeys(matched_handlers))

    @classmethod
    def ready(cls, **data: Unpack[BusInput]) -> Self:
        bus: Self = cls()
        spec = BusSpec(**data)

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


# @lru_cache(maxsize=256)
# def _get_patterns(
#     event: EventName, active_patterns: tuple[EventPattern, ...]
# ) -> tuple[EventPattern, ...]:  # tuple for lru_cache (immutable)
#     """Match pattern and cache results decoupled from the Bus"""
#     return tuple(
#         pattern
#         for pattern in active_patterns
#         if fnmatch.fnmatch(event, pattern)
#     )
