"""
Typed, ergonomic facade on top of the EventBus.

- Mirrors common printer + logger patterns
- Provides local functor factories
- Keeps printer focused on rendering only
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..contract.cli import PanelDTO, TableDTO
from ..contract.event import EmitFunc, EventName
from ..contract.log import LogDTO
from .bus import EventBus


@dataclass(frozen=True)
class EmitFunctor:
    """Pre-bound, specialized emitter for frequent use cases"""

    emit: EmitFunc
    event_name: EventName
    sender: str
    defaults: dict[str, Any] = field(default_factory=dict)

    def __call__(self, **overrides: Any):
        payload: dict[str, Any] = {**self.defaults, **overrides}
        self.emit(self.event_name, self.sender, **payload)

    def __str__(self):
        return f"EmitBusFunc({self.sender} → {self.event_name})"


@dataclass(frozen=True)
class Emitter:  # TESTING: new and untested!
    """Provide unified and simple access to Bus"""

    bus: EventBus

    def __call__(
        self, event_name: EventName, sender: str, **payload: Any
    ) -> None:
        """Low-level escape hatch"""
        self.bus.emit(event_name, sender, **payload)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Log shortcuts (testing...)
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    # TODO: Factory that deploys this log block,
    # but with filled sender, maybe event_name
    def log(
        self,
        event: EventName,
        message: str,
        sender: str,
        level: str = "DEBUG",
        **extra,
    ):
        dto = LogDTO(message=message, level=level, extra=extra or {})
        self(event, sender, target=dto)

    def info(self, event: EventName, message: str, sender: str, **extra):
        self.log(event, message, sender, "INFO", **extra)

    def warning(self, event: EventName, message: str, sender: str, **extra):
        self.log(event, message, sender, "WARNING", **extra)

    def error(self, event: EventName, message: str, sender: str, **extra):
        self.log(message, "ERROR", **extra)

    def success(self, event: EventName, message: str, sender: str, **extra):
        self.log(message, "SUCCESS", **extra)

    # error, debug, success...

    def panel(self, text: str | list[str], **kwargs):
        dto = PanelDTO.from_call(text=text, **kwargs)
        self.bus.emit("ui.panel", self.default_sender, target=dto)

    def table(self, **kwargs):  # or specific from_ helpers
        dto = TableDTO.from_call(**kwargs)
        self.bus.emit("ui.table", self.default_sender, target=dto)

    # md, line, rule, etc. — only the ones you use often

    def make(
        self, event_name: EventName, sender: str, **defaults: Any
    ) -> EmitFunctor:
        """Factory for local specialized emitters"""
        return EmitFunctor(
            emit=self.bus.emit,
            event_name=event_name,
            sender=sender,
            defaults=defaults,
        )

    # Example high-level helpers
    def make_log(self, level: str = "INFO", **defaults) -> EmitFunctor:
        return self.make("sys.log", level=level, **defaults)

    def make_panel(self, **defaults) -> EmitFunctor:
        return self.make("ui.panel", **defaults)


class _DataOperator:
    """Example for Usage, do not use from here!"""

    def __init__(self, make_emitter: Callable[..., EmitFunctor]):
        self.emit_ui: EmitFunctor = make_emitter(
            "cli.render.panel", sender="DataOp"
        )

    def process(self, result_dict: dict[str, Any]):
        dto = PanelDTO.from_call(
            text="Operation Successful", metrics=result_dict, frame="green"
        )
        self.emit_ui(target=dto)
