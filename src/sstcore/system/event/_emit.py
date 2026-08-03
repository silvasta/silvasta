"""
Provide ergonomic facade on top of the EventBus

- Mirror common printer + logger patterns
- Provide local functor factories
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "Emitter",
    "LogEmitter",
    "ViewEmitter",
    "EmitFunctor",
]

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ...port.event import EventBus
from ...port.event._emit import Emitter as Emitter_
from ...port.event.name import CliEvent, EventName
from ...utils.print.core import EmitterCore
from ...utils.print.mixin import (
    BoxMixin,
    HeaderMixin,
    LineMixin,
    PanelMixin,
    TableMixin,
)
from ...utils.view import Repr, Str, view


# TASK: this as utils, inside system.utils.emit?
class _CliEmitter(  # TESTING: ideas for printer "inversion"
    HeaderMixin,
    BoxMixin,
    LineMixin,
    TableMixin,
    PanelMixin,
    EmitterCore,
):
    """Wait for final composition in a few days or weeks"""


@dataclass(frozen=True)
@view(str=Str.SHORT, repr=Repr.BOX)  # TODO: others?
class Emitter:
    # TASK: this as assembler, inside system.event._emit?
    """Lead the Distribution of globally wired Bus Entry Points"""

    bus: EventBus

    def __call__(self, event: EventName, sender: str, **payload: Any) -> None:
        self.bus.emit(event, sender, **payload)

    # --- Factory methods ---
    # LATER: Emitter.view as instance ViewEmitter
    # def view(
    #     self,
    #     event: EventName,
    #     sender: str,
    #     target: Any,
    #     *,
    #     level: str = "INFO",
    # ) -> None:
    #     self(event, sender, **ViewEmitter.build_payload(target, level=level))

    def make_log(self, event: EventName, sender: str) -> LogEmitter:
        # LATER: Emitter.log.make(...)
        return LogEmitter(self, sender, event)

    def make_view(
        self, sender: str, *, event: EventName = CliEvent.RENDER
    ) -> ViewEmitter:
        # LATER: Emitter.view.make(...)
        return ViewEmitter(self, sender, event)

    # --- Direct logging helpers (for one-off usage) ---

    # --- View / Render helpers ---

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
