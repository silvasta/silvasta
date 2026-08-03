"""
Define the Structure of Event Sending Helpers

EmitFunc: minimal requirements for Bus call

"""

__all__: list[str] = [
    "BusEmit",
    "Emit",
    "EventEmit",
    #
    "LogEmit",
    "EventLogEmit",  # TODO:check
    "LogEmitter",
    #
    "ViewEmitter",
    #
    "Emitter",
]

from typing import Any, Protocol

from .name import EventName


class BusEmit(Protocol):
    """Define function as it is used in EventBus (using event_name)"""

    def __call__(
        self, event_name: EventName, sender: str, **payload: Any
    ) -> None: ...


class Emit(Protocol):
    """Call to EventBus"""

    def __call__(
        self, event: EventName, sender: str, **payload: Any
    ) -> None: ...


class EventEmit(Protocol):
    """Call to Bus with pre-defined args"""

    event: EventName
    sender: str

    def __call__(self, **payload: Any) -> None: ...


class LogEmit(Protocol):
    """Log to EventBus"""

    def __call__(
        self,
        event: EventName,
        sender: str,
        message: str,
        *,
        level: str = "INFO",
        **extra: Any,
    ) -> None: ...


class EventLogEmit(Protocol):
    """Bind Event and Sender for logs to Bus"""

    event: EventName
    sender: str

    def __call__(
        self, message: str, *, level: str = "INFO", **extra: Any
    ) -> None: ...


class LogEmitter[LogEmitT: LogEmit | EventLogEmit](Protocol):
    """Provide log calls to Bus"""

    __call__: LogEmitT
    debug: LogEmitT
    info: LogEmitT
    warning: LogEmitT
    error: LogEmitT
    success: LogEmitT


class ViewEmitter(Protocol):
    event: EventName
    sender: str
    __call__: EventEmit

    @staticmethod
    def build_payload(
        target: Any, *, level: str = "INFO"
    ) -> dict[str, Any]: ...


# IDEA: this as FactoryMixin, as well for LogEmitter
class Emitter[EmitT: Emit | EventEmit](LogEmitter, Protocol):
    __call__: EmitT

    def bind(
        self, event: EventName, sender: str, **defaults: Any
    ) -> Emitter[EventEmit]: ...

    def make(self, **defaults: Any) -> Emitter[Emit]: ...
