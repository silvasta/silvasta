"""
Provide ergonomic facade on top of the EventBus

- Mirror common printer + logger patterns
- Provide local functor factories
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "Emitter",
]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ...brick.view import Repr, Str, view
from ...port.event import EventBus
from ...port.event._emit import Emitter as Emitter_
from ...port.event.name import CliEvent, EventName
from ...util.emit import LogEmitter, ViewEmitter


@dataclass(frozen=True)
@view(str=Str.SHORT, repr=Repr.BOX)  # TODO: others?
class Emitter:
    # TASK: this as assembler, inside system.event._emit?
    """Lead the Distribution of globally wired Bus Entry Points"""

    bus: EventBus

    def __call__(self, event: EventName, sender: str, **payload: Any) -> None:
        self.bus.emit(event, sender, **payload)

    # REMOVE: replace by LogEmitter
    def make_log(self, event: EventName, sender: str) -> LogEmitter:
        # LATER: Emitter.log.make(...)
        return LogEmitter(self, sender, event)

    # REMOVE: replace by CliEmitter
    def make_view(
        self, sender: str, *, event: EventName = CliEvent.RENDER
    ) -> ViewEmitter:
        # LATER: Emitter.view.make(...)
        return ViewEmitter(self, sender, event)

    def view(
        # LATER: Emitter.view as instance ViewEmitter
        self,
        event: EventName,
        sender: str,
        target: Any,
        *,
        level: str = "INFO",
    ) -> None:
        self(event, sender, **ViewEmitter.build_payload(target, level=level))

    @property
    def _repr_box_text(self) -> str:
        return repr(self.bus)


if TYPE_CHECKING:
    from typing import cast

    bus: EventBus = cast(EventBus, object())
    _instance_check: Emitter_ = Emitter(bus)
    _class_check: type[Emitter_] = Emitter
