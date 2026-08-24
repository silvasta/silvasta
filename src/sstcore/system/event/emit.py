"""
Provide ergonomic facade on top of the EventBus

- Mirror common printer + logger patterns
- Provide local functor factories
                                                       DependencyLevel[X]
"""

from collections.abc import Callable

from sstcore.port.view import CliRenderable, LogSerializable

__all__: list[str] = [
    "Emitter",
    "LogEmitter",
    "ViewEmitter",
]
# REFACTOR:
# REFACTOR:
# REFACTOR:
# REFACTOR:
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ...brick.view import Repr, Str, view
from ...port.event.dto import LogDTO
from ...port.event.emit import (
    #
    BoundEmit,
    BoundEmitted,
    BoundLogEmitted,
    Emit,
    LogEmit,
    LogEmitted,
    UnboundEmit,
)
from ...port.event.name import CliEvent, EventName


class EventEmitter:
    """Bind Emit Context for 1 Purpose and Task"""

    emit: Emit
    event: EventName
    sender: str
    defaults: dict[str, Any] = field(default_factory=dict)

    def __call__(self, **payload: Any) -> None:
        self.emit(self.event, self.sender, **{**self.defaults, **payload})


if TYPE_CHECKING:
    _class_check: type[BoundEmitted] = EventEmitter


class LogLevelMixin:
    """Share level-specific logging logic depending on child class __call__"""

    def debug(self: Callable, *args: Any, **extra: Any) -> None:
        self(*args, level="DEBUG", **extra)

    def info(self: Callable, *args: Any, **extra: Any) -> None:
        self(*args, level="INFO", **extra)

    def warning(self: Callable, *args: Any, **extra: Any) -> None:
        self(*args, level="WARNING", **extra)

    def error(self: Callable, *args: Any, **extra: Any) -> None:
        self(*args, level="ERROR", **extra)

    def success(self: Callable, *args: Any, **extra: Any) -> None:
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


_log: type[BoundLogEmitted] = EventLogEmitter
_log: type[LogEmit] = EventLogEmitter


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


_log: type[LogEmitted] = FullLogEmitter


@view(Str.SHORT, Repr.BOX)
class _EmitterView:
    sender: str
    event: EventName

    @property
    def _repr_box_text(self):
        return f"{self.sender}  {self.event!r}"


class ViewEmitter(_EmitterView):
    """Bind Emit Context for 1 CLI and Log Session"""

    emit: BoundEmit
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

        # EXTRACT:
        # EXTRACT:
        # EXTRACT:
        payload: dict[str, Any] = {}

        if isinstance(target, CliRenderable):
            payload["cli"] = target.__cli__()

        if isinstance(target, LogSerializable):
            payload["log"] = target.__log__()

        return payload or {"log": LogDTO(message=str(target), level=level)}


@dataclass(frozen=True)
@view(str=Str.SHORT, repr=Repr.BOX)
class Emitter(LogLevelMixin):
    """Lead the Distribution of globally wired Bus Entry Points"""

    emit: Emit

    log: FullLogEmitter = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "log", FullLogEmitter(self.emit))

    def __call__(self, event: EventName, sender: str, **payload: Any) -> None:
        self.emit(event, sender, **payload)

    def bind(
        self, event: EventName, sender: str, **defaults: Any
    ) -> UnboundEmit:
        """Create a specialized, pre-bound emitter."""
        return EventEmitter(self.emit, event, sender, defaults)

    def view(
        self, sender: str, event: EventName = CliEvent.RENDER
    ) -> ViewEmitter:
        """Create a CLI/Log hybrid emitter for complex objects."""
        return ViewEmitter(
            emit=self.bind(event, sender), sender=sender, event=event
        )


if TYPE_CHECKING:
    _instance_check: Emitter_ = Emitter()
    _class_check: type[Emitter_] = Emitter
