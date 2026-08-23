"""
Provide ergonomic facade on top of the EventBus

- Mirror common printer + logger patterns
- Provide local functor factories
                                                       DependencyLevel[X]
"""

__all__: list[str] = [
    "Emitter",
    "LogEmitter",
    "ViewEmitter",
]
# REFACTOR:
# REFACTOR:
# REFACTOR:
# REFACTOR:
# REFACTOR:
# REFACTOR:
# REFACTOR:
# REFACTOR:
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sstcore.port.printer import Protocol

from ...brick.view import Repr, Str, view
from ...port.event import LogDTO
from ...port.event._emit import (
    Emit,
    EventEmit,
    EventLogEmit,
    LogEmit,
    LogEmitter,
)
from ...port.event._emit import Emitter as Emitter_
from ...port.event.name import CliEvent, EventName


@view(str=Str.SHORT, repr=Repr.BOX)
# AI: this for bounded emits
class _EmitterView:
    sender: str
    event: EventName

    @property
    def _repr_box_text(self):
        return f"{self.sender}  {self.event!r}"


@dataclass(frozen=True)
# AI: this for bind on raw emitter
class EventEmitter:  # REMOVE: ??
    """Bind Emit Context for 1 Purpose and Task"""

    emit: Emit
    event: EventName
    sender: str
    defaults: dict[str, Any] = field(default_factory=dict)

    def __call__(self, **payload: Any) -> None:
        self.emit(self.event, self.sender, **{**self.defaults, **payload})


if TYPE_CHECKING:
    _class_check: type[EventEmit] = EventEmitter


class _RequiresCall(Protocol):
    """Dummy Protocol so the Mixin knows `self` has a __call__ accepting `level`."""

    def __call__(self, *args: Any, level: str, **kwargs: Any) -> None: ...


class LogLevelMixin:
    """Share level-specific logging logic depending on child class __call__"""

    def debug(self: _RequiresCall, *args: Any, **extra: Any) -> None:
        self(*args, level="DEBUG", **extra)

    def info(self: _RequiresCall, *args: Any, **extra: Any) -> None:
        self(*args, level="INFO", **extra)

    def warning(self: _RequiresCall, *args: Any, **extra: Any) -> None:
        self(*args, level="WARNING", **extra)

    def error(self: _RequiresCall, *args: Any, **extra: Any) -> None:
        self(*args, level="ERROR", **extra)

    def success(self: _RequiresCall, *args: Any, **extra: Any) -> None:
        self(*args, level="SUCCESS", **extra)


class EventLogEmitter(LogLevelMixin):
    emit: Emit
    event: EventName
    sender: str

    def __call__(
        self, message: str, *, level: str = "INFO", **extra: Any
    ) -> None:
        dto = LogDTO(message=message, level=level, extra=extra)
        self.emit(self.event, self.sender, log=dto)


_log: type[EventLogEmit] = EventLogEmitter
_log: type[LogEmitter] = EventLogEmitter


@dataclass(frozen=True)
class FullLogEmitter(LogLevelMixin):
    emit: Emit

    def __call__(
        self,
        event: EventName,
        sender: str,
        message: str,
        *,
        level: str = "INFO",
        **extra: Any,
    ) -> None:
        dto = LogDTO(message=message, level=level, extra=extra)
        self.emit(event, sender, log=dto)


_log: type[LogEmit] = FullLogEmitter
_log: type[LogEmitter[LogEmit]] = FullLogEmitter


# @dataclass(frozen=True)
class ViewEmitter(_EmitterView):
    """Bind Emit Context for 1 CLI and Log Session"""

    emit: EventEmit
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


class EmitMaker:
    emit: EventEmit

    def make(self, event: EventName, sender: str, **defaults: Any) -> Emitter:
        return type(self)(  # AI: something  like this
            self.emit, event, sender, defaults
        )

    def bind(
        self, event: EventName, sender: str, **defaults: Any
    ) -> EventEmitter:
        return Emitter(self.emit, event, sender, defaults)  # AI: or emit


@dataclass(frozen=True)
@view(str=Str.SHORT, repr=Repr.BOX)  # TODO: others?
class Emitter(LogLevelMixin):
    """Lead the Distribution of globally wired Bus Entry Points"""

    def __call__(self, event: EventName, sender: str, **payload: Any) -> None:
        self.emit(event, sender, **payload)

    emit: Emit

    log: LogEmitter[LogEmit]  # AI: this or Mixin


if TYPE_CHECKING:
    _instance_check: Emitter_ = Emitter()
    _class_check: type[Emitter_] = Emitter
