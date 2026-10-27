"""
Define the Shape of the Event Bus Caller

                              DependencyLevel.sstcore.port.event[2]
"""

__all__: list[str] = [
    "Emit",
    "Emitting",
    "BoundEmit",
    #
    "LogEmit",
    "Log",
]

from typing import Any as _Any
from typing import Protocol as _Protocol

from ._core import EventBus as _EventBus
from .name import EventName as _EventName


class Emit(_Protocol):
    """Define the Structure of the Emitter"""

    @property
    def __call__(self) -> Emitting: ...

    bus: _EventBus
    log: LogEmit
    # IDEA: mount the EventDtoFactory! (latest in implementation)

    def make(self, **defaults) -> LogEmit: ...
    def bind(self, event: _EventName, sender: str, **kwargs) -> BoundEmit: ...


class Emitting(_Protocol):
    def __call__(
        self, event: _EventName, /, *, sender: str, **payload
    ) -> _Any | None:
        """Default Call to EventBus"""


class BoundEmit(_Protocol):
    def __call__(self, **payload) -> _Any | None:
        """Call to EventBus with predefined Event and Sender"""


class Log(_Protocol):
    def __call__(
        self,
        message: str,
        /,
        *,
        event: _EventName,
        sender: str,
        level: str = "INFO",
        **extra,
    ) -> _Any | None:
        """Log to EventBus"""


class LogEmit(_Protocol):
    """Call to Bus with predefined log emits"""

    @property
    def __call__(self) -> Log: ...
    @property
    def debug(self) -> Log: ...
    @property
    def info(self) -> Log: ...
    @property
    def warning(self) -> Log: ...
    @property
    def error(self) -> Log: ...
    @property
    def success(self) -> Log: ...
