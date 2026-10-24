"""
Build the Event Handler Container

                            DependencyLevel.sstcore.system.event[1]
"""

__all__: list[str] = [
    "BusRegistry",
]

import fnmatch
from collections.abc import Callable
from typing import Any

from ...brick.reflect import objname
from ...brick.vault import ListVault
from ...port.event import Event
from ...port.event.name import EventName, EventPattern
from ...port.link import portlink
from ...port.register import FuncRegister, ListRegister
from ._handler import EventHandler

type EventFunc = Callable[[Event], None]
type EventDecorator = Callable[[EventFunc], EventFunc]


@portlink(FuncRegister)
@portlink(ListRegister)
class BusRegistry(ListVault[EventHandler]):
    """
    Collect and Provide EventHandlers for the EventBus

    - Attach by EventHandler instance, function, or @attach Decorator
    - Resolve matching handlers by EventName and wildcard pattern
    """

    def _item_id(self, item: EventHandler, /) -> tuple[str, EventPattern]:
        """Unique identity is (handler name, subscribed pattern)."""
        # INFO: BaseFunctor assigns __name__ = name
        return (item.__name__, item.pattern)  # CHECK:

    def _normalize(self, value: Any) -> EventHandler:
        """Ensure incoming items are valid EventHandler instances."""
        if isinstance(value, EventHandler):
            return value
        if callable(value) and not isinstance(value, type):
            # IDEA: EventHandler(call=value) ??
            return EventHandler.from_func(value)
        raise TypeError(
            f"Expected EventHandler or handler function, got {objname(value)}"
        )

    def attach(
        self,
        pattern: EventPattern = "*",
        *,
        fail_loud: bool = False,
        name: str = "",
    ) -> EventDecorator:
        """Attach handler functions by decorator."""

        def decorator(func: EventFunc) -> EventFunc:
            handler = EventHandler.from_func(
                func,
                pattern=pattern,
                fail_loud=fail_loud,
                name=name,
            )
            self.add(handler)
            return func

        return decorator

    def resolve(self, event: EventName) -> list[EventHandler]:
        """Return all handlers whose pattern matches the given EventName."""
        # LATER: do this inside Vault where it has more effect
        # - here it just scratches the surface
        # - completely remove Registry.resolve, was never desired
        # - Registry.find or Registry[...] intended for access, nothing else
        # Exactly something like this:
        # registry[lambda h: h.handles(event)] or registry.find(lambda h: h.pattern == "*")
        # ...but without lambda! that should be wired internally
        return self._where(
            lambda h: h.pattern == "*" or fnmatch.fnmatch(event, h.pattern)
        )
