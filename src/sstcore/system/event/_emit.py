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

from dataclasses import dataclass, field
from typing import Any

from ...port.cli import CliRenderable
from ...port.event import CliEvent, EmitFunc, EventName
from ...port.log import LogDTO, LogSerializable
from ...utils.print.core import EmitterCore
from ...utils.print.mixin import (
    BoxMixin,
    HeaderMixin,
    LineMixin,
    PanelMixin,
    TableMixin,
)
from ...utils.view import Repr, Str, view
from ._bus import EventBus


@view(str=Str.SHORT, repr=Repr.BOX)
class _EmitterView:
    @property
    def _repr_box_text(self):
        return f"{self.sender}  {self.event!r}"  # ty:ignore


@dataclass(frozen=True)
class EmitFunctor(_EmitterView):
    """Bind Emit Context for 1 Purpose and Task"""

    emit: EmitFunc
    sender: str
    event: EventName
    defaults: dict[str, Any] = field(default_factory=dict)

    def __call__(self, **overrides: Any) -> None:
        self.emit(self.event, self.sender, **{**self.defaults, **overrides})


@dataclass(frozen=True)
class LogEmitter(_EmitterView):
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
class ViewEmitter(_EmitterView):
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


class _CliEmitter(  # TESTING: ideas for printer "inversion"
    HeaderMixin, BoxMixin, LineMixin, TableMixin, PanelMixin, EmitterCore
):
    """Wait for final composition in a few days or weeks"""


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
