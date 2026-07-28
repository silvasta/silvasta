"""
Typed, ergonomic facade on top of the EventBus.

- Mirrors common printer + logger patterns
- Provides local functor factories
- Keeps printer focused on rendering only

"""

from ..utils.print.core import EmitterCore
from ..utils.print.mixin import (
    BoxMixin,
    HeaderMixin,
    LineMixin,
    PanelMixin,
    TableMixin,
)

__all__: list[str] = [
    "EmitFunctor",
    "LogEmitter",
    "ViewEmitter",
    "Emitter",
]

from dataclasses import dataclass, field
from typing import Any

from ..port.cli import CliRenderable
from ..port.event import CliEvent, EmitFunc, EventName
from ..port.log import LogDTO, LogSerializable
from .bus import EventBus


class _ViewMixin:
    def __str__(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
        return f"{self}[{self.sender}  {self.event!r}]"  # ty:ignore


@dataclass(frozen=True)
class EmitFunctor(_ViewMixin):
    """Bind Emit Context for 1 Purpose and Task"""

    emit: EmitFunc
    sender: str
    event: EventName
    defaults: dict[str, Any] = field(default_factory=dict)

    def __call__(self, **overrides: Any) -> None:
        self.emit(self.event, self.sender, **{**self.defaults, **overrides})


@dataclass(frozen=True)
class LogEmitter(_ViewMixin):
    """Bind Emit Context for 1 Log Session"""

    emit: EmitFunc
    sender: str
    event: EventName

    def __call__(
        self, message: str, *, level: str = "INFO", **extra: Any
    ) -> None:
        self.emit(
            event=self.event,
            sender=self.sender,
            log=LogDTO(message=message, level=level, extra=extra),
        )

    def debug(self, message: str, **extra: Any) -> None:
        self(message, level="DEBUG", **extra)

    def info(self, message: str, **extra: Any) -> None:
        self(message, level="INFO", **extra)

    def warning(self, message: str, **extra: Any) -> None:
        self(message, level="WARNING", **extra)

    def error(self, message: str, **extra: Any) -> None:
        self(message, level="ERROR", **extra)

    def success(self, message: str, **extra: Any) -> None:
        self(message, level="SUCCESS", **extra)


@dataclass(frozen=True)
class ViewEmitter(_ViewMixin):
    """Bind Emit Context for 1 CLI and Log Session"""

    emit: EmitFunc
    sender: str
    event: EventName = CliEvent.RENDER

    def __call__(
        self,
        target: Any,
        *,
        event: EventName | None = None,
        level: str = "INFO",
    ) -> None:
        self.emit(
            event=event or self.event,
            sender=self.sender,
            **self.build_payload(target, level=level),
        )

    @staticmethod
    def build_payload(target: Any, *, level: str = "INFO") -> dict[str, Any]:
        """Extract Log and Cli DTOs or default to flat string log"""

        payload: dict[str, Any] = {}

        if isinstance(target, CliRenderable):
            payload["cli"] = target.__cli__()

        if isinstance(target, LogSerializable):
            payload["log"] = target.__log__()

        return payload or {"log": LogDTO(message=str(target), level=level)}


class CliEmitter(
    HeaderMixin, BoxMixin, LineMixin, TableMixin, PanelMixin, EmitterCore
):
    """Wait for final composition in a few days or weeks"""


# ERROR: would have been a surprise if that worked without issues...
# - maybe a modication of the print.blueprint can fix the issues
#    ~/PolyBox/Code/sstcore/latest/src/sstcore/system/  1
#   └╴󰌠  emit.py  1
#     └╴  Argument to bound method `PanelMixin.panel` is incorrect: Expected `Printer`, found `CliEmitter`
#          info: type `CliEmitter` is not assignable to protocol `Printer`
#          info: └── protocol member `__call__` is incompatible
#          info:     └── incompatible return types: `CliDTO | LogDTO | None` is not assignable to `None`
#          info:         └── element `CliDTO` of union `CliDTO | LogDTO | None` is not assignable to `None` ty (invalid-argument-type) [133, 1]
# cli_emit = CliEmitter()
# cli_emit.panel(target="test")
# AI: Important! The CliEmitter is just a quick test, no time to focus deeply on it now.
# - maybe a quick statement too the EmitterCore approach would be fine (see utils.print.core)


@dataclass(frozen=True)
class Emitter:
    """Lead the Distribution of globally wired Bus Entry Points"""

    def __str__(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
        return f"{self}[{self.bus!r}]"

    bus: EventBus

    def __call__(self, event: EventName, sender: str, **payload: Any) -> None:
        self.bus.emit(event, sender, **payload)

    # --- Factory methods ---

    def make(
        self, event: EventName, sender: str, **defaults: Any
    ) -> EmitFunctor:
        return EmitFunctor(self, sender, event, defaults)

    def make_log(self, event: EventName, sender: str) -> LogEmitter:
        return LogEmitter(self, sender, event)

    def make_view(
        self, sender: str, *, event: EventName = CliEvent.RENDER
    ) -> ViewEmitter:
        return ViewEmitter(self, sender, event)

    # --- Direct logging helpers (for one-off usage) ---

    def log(
        self,
        event: EventName,
        sender: str,
        message: str,
        *,
        level: str = "INFO",
        **extra: Any,
    ) -> None:
        self(
            event=event,
            sender=sender,
            log=LogDTO(message=message, level=level, extra=extra),
        )

    def info(
        self, event: EventName, sender: str, message: str, **extra: Any
    ) -> None:
        self.log(event, sender, message, level="INFO", **extra)

    def warning(
        self, event: EventName, sender: str, message: str, **extra: Any
    ) -> None:
        self.log(event, sender, message, level="WARNING", **extra)

    def error(
        self, event: EventName, sender: str, message: str, **extra: Any
    ) -> None:
        self.log(event, sender, message, level="ERROR", **extra)

    def success(
        self, event: EventName, sender: str, message: str, **extra: Any
    ) -> None:
        self.log(event, sender, message, level="SUCCESS", **extra)

    # --- View / Render helpers ---

    def view(
        self,
        event: EventName,
        sender: str,
        target: Any,
        *,
        level: str = "INFO",
    ) -> None:
        self(event, sender, **ViewEmitter.build_payload(target, level=level))
