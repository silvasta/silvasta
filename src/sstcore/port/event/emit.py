"""
Define the Shape of the Event Bus Caller

                              DependencyLevel.sstcore.port.event[2]
"""

__all__: list[str] = [
    "Emit",
    "Emitting",
    "BoundEmit",
    #
    "Log",
    "BoundLog",
    "LogEmit",
]

from typing import Any as _Any
from typing import Protocol as _Protocol

from ._core import EventBus as _EventBus
from .factory import EventDtoFactory as _EventDtoFactory
from .name import EventName as _EventName


class Emitting(_Protocol):
    def __call__(
        self, event: _EventName, /, *, sender: str, **payload
    ) -> _Any | None:
        """Default Call to EventBus"""


class Emit(_Protocol):
    """Define the Structure of the Emitter"""

    @property
    def bus(self) -> _EventBus: ...
    @property
    def dto(self) -> _EventDtoFactory: ...
    @property
    def log(self) -> LogEmit: ...

    def __call__(
        self, event: _EventName, /, *, sender: str, **payload: _Any
    ) -> None:
        """Fire an Event on the Bus"""

    def bind(
        self, event: _EventName, sender: str, /, **defaults: _Any
    ) -> BoundEmit:
        """Create a pre-bound Emitter for a specific EventName and sender."""

    def make(
        self, event: _EventName | None = None, sender: str = ""
    ) -> LogEmit:
        """Create a pre-bound LogEmitter for a specific EventName and sender."""


class BoundEmit(_Protocol):
    """Pre-bound Emitter for a specific (event, sender) context."""

    @property
    def event(self) -> _EventName: ...
    @property
    def sender(self) -> str: ...

    def __call__(self, **payload: _Any) -> None:
        """Fire pre-bound Event with payload"""


class Log(_Protocol):
    def __call__(
        self,
        message: str,
        /,
        *,
        event: _EventName,
        sender: str,
        level: str = "INFO",
        metrics: dict[str, _Any] | None = None,
        **extra: _Any,
    ) -> None:
        """Unbound Log call to EventBus"""


class BoundLog(_Protocol):
    def __call__(
        self,
        message: str,
        /,
        *,
        level: str = "INFO",
        metrics: dict[str, _Any] | None = None,
        **extra: _Any,
    ) -> None:
        """Pre-bound Log call to EventBus"""


class LogEmit[Logging: Log | BoundLog](_Protocol):
    """Call to Bus with predefined log emits"""

    @property
    def __call__(self) -> Logging: ...
    @property
    def debug(self) -> Logging: ...
    @property
    def info(self) -> Logging: ...
    @property
    def warning(self) -> Logging: ...
    @property
    def error(self) -> Logging: ...
    @property
    def success(self) -> Logging: ...
