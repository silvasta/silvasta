"""
Provide ergonomic facade on top of the EventBus

- Mirror common printer + logger patterns
- Provide local functor factories
                                                       DependencyLevel[X]
"""

__all__: list[str] = [
    "Emitter",
    "LogEmitter",
]
from dataclasses import dataclass
from typing import Any

from ...forge.view import view
from ...forge.view.catalog import Repr, Str
from ...forge.view.factory import dto_factory
from ...port.event._core import EventBus
from ...port.event.dto import LogDTO
from ...port.event.emit import BoundEmit, BoundLog, Emit, Emitting, LogEmit
from ...port.event.factory import EventDtoFactory, LogDelivering
from ...port.event.name import EventName, LogEvent
from ...port.link import portlink


@dataclass(frozen=True, slots=True)
@view(Str.SHORT, Repr.BOX)
class _EmitView:
    sender: str
    event: EventName

    @property
    def _repr_box_text(self):
        return f"{self.sender}  {self.event!r}"


@portlink(LogEmit)
@dataclass
class LogEmitter:
    """Unbound Log Emitter: requires `event` and `sender` at call time."""

    emit: Emitting
    producer: LogDelivering
    event: EventName | None = None
    sender: str = ""

    def __call__(
        self,
        message: str,
        /,
        *,
        event: EventName | None = None,
        sender: str = "",
        level: str = "INFO",
        metrics: dict[str, Any] | None = None,
        **extra,
    ) -> None:
        event: EventName = event or self.event or LogEvent.NONE
        sender: str = sender or self.sender or repr(self)
        dto: LogDTO = self.producer(
            message,
            level=level,
            metrics=metrics or {},
            extra=extra,
        )
        self.emit(event, sender=sender, log=dto)

    def debug(self, message: str, /, **kwargs) -> None:
        self(message, level="DEBUG", **kwargs)

    def info(self, message: str, /, **kwargs) -> None:
        self(message, level="INFO", **kwargs)

    def warning(self, message: str, /, **kwargs) -> None:
        self(message, level="WARNING", **kwargs)

    def error(self, message: str, /, **kwargs) -> None:
        self(message, level="ERROR", **kwargs)

    def success(self, message: str, /, **kwargs) -> None:
        self(message, level="SUCCESS", **kwargs)


@portlink(BoundEmit)
@dataclass(frozen=True, slots=True)
class BoundEmitter(_EmitView):
    """Pre-bound Log Emitter: `event` and `sender` are already locked in."""

    emit: Emitting
    event: EventName
    sender: str

    def __call__(self, **payload) -> None:
        self.emit(self.event, sender=self.sender, **payload)


@portlink(Emit)
@dataclass(frozen=True, slots=True)
class Emitter:
    """Lead the Distribution of globally wired Bus Entry Points"""

    bus: EventBus
    dto: EventDtoFactory = dto_factory
    log: LogEmitter  # AI_TASK: default for this needed

    @property
    def emit(self) -> Emitting:
        return self.bus.emit

    # REMOVE: log is intended to give access to unbound log emitter!
    # @property
    # def log(self) -> LogEmitter:
    #     return LogEmitter(emit=self.bus.emit, dto=self.dto)

    def __call__(self, event: EventName, /, *, sender: str, **payload) -> None:
        self.bus.emit(event, sender=sender, **payload)

    def bind(self, event: EventName, sender: str, /) -> BoundEmit:
        """Create a specialized, pre-bound emitter for `(event, sender)`."""
        return BoundEmitter(
            emit=self.bus.emit,
            event=event,
            sender=sender,
        )

    def make(
        self, event: EventName | None = None, sender: str = ""
    ) -> LogEmit[BoundLog]:
        """Create a pre-bound `BoundLogEmitter` for `(event, sender)`."""
        return LogEmitter(
            emit=self.bus.emit,
            event=event,
            sender=sender,
            producer=self.dto.log,
        )
