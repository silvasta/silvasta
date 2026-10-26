"""
Build the Event Handler Container

                            DependencyLevel.sstcore.system.event[1]
"""

__all__: list[str] = [
    "BusRegistry",
]

from collections.abc import Callable
from typing import Any

from ...brick.reflect import objname
from ...brick.vault import ListVault
from ...port.event import Event
from ...port.event.name import EventPattern
from ...port.link import portlink
from ...port.register import FuncRegister, ListRegister
from ._handler import EventHandler

type EventFunc = Callable[[Event], None]
type EventDecorator = Callable[[EventFunc], EventFunc]


@portlink(FuncRegister)
@portlink(ListRegister)
class BusRegistry(ListVault[EventHandler, str]):
    """
    Collect and Provide EventHandlers for the EventBus

    - Attach by EventHandler instance, function, or @attach Decorator
    - Find matching handlers via registry.find(event)
    - Access specific handler by name via registry["HandlerName"]

    """

    def _normalize(self, value: Any) -> EventHandler:
        """Ensure incoming items are valid EventHandler instances."""
        if isinstance(value, EventHandler):
            return value
        if callable(value) and not isinstance(value, type):
            return EventHandler(call=value)
        raise TypeError(
            f"Expected EventHandler or handler function, got {objname(value)}"
        )

    def _box_key(self, key: Event | EventPattern) -> list[EventHandler]:
        """Provide all matching handlers - hook for find(..) and count(..)"""
        return [handler for handler in self.vault if handler.handles(key)]

    def _item_id(self, item: EventHandler, /) -> str:
        return item.__name__

    def _key_item(self, key: str) -> EventHandler:
        """Provide handler by __name__ or full id - hook for registry[..]"""
        found: list[EventHandler] = [
            handler  #
            for handler in self.vault
            if handler.__name__ == key or handler._base_name == key
        ]
        if len(found) != 1:
            raise KeyError(f"Duplicated Handler for {key=}! {found=}")
        return found[0]

    def attach(
        self,
        pattern: EventPattern = "*",
        *,
        fail_loud: bool = False,
        name: str = "",
    ) -> EventDecorator:
        """Attach handler functions by decorator."""

        def decorator(func: EventFunc) -> EventFunc:
            handler = EventHandler(
                call=func,
                pattern=pattern,
                fail_loud=fail_loud,
                name=name,
            )
            self.add(handler)  # LATER: check if duplicate?
            return func

        return decorator
