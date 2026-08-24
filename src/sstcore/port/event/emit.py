"""
Define the Shape of the Event Bus Calling

-
"""

__all__: list[str] = [
    # Type Aliases
    # Raw Callables (Unbound)
    # Bound Callables
    # Facade / Composite Emitters
]
__all__: list[str] = [
    "Emit",
    "Emitter",
    "BoundEmit",
    #
    "LogEmit",
    "EventLog",
    "LogEmitter",
    "Log",
    #
    "CliEmit",
    "CliPrint",
    "CliEmitter",
    "Print",
]

from typing import Any as _Any
from typing import Protocol as _Protocol

from .name import EventName as _EventName

type Print = CliEmit | CliPrint
type Log = LogEmit | EventLog


class Emit(_Protocol):
    def __call__(self, event: _EventName, sender: str, **payload) -> None:
        """Call to EventBus"""


class LogEmit(_Protocol):
    def __call__(
        self,
        event: _EventName,
        sender: str,
        message: str,
        *,
        level: str = "INFO",
        **extra,
    ) -> None:
        """Log to EventBus"""


class EventLog(_Protocol):
    def __call__(self, message: str, *, level: str = "INFO", **extra) -> None:
        """Maximally bound Log call to EventBus"""


class LogEmitter[LogEmiT: Log](_Protocol):
    """Call to Bus with predefined log emits"""

    __call__: LogEmiT
    debug: LogEmiT
    info: LogEmiT
    warning: LogEmiT
    error: LogEmiT
    success: LogEmiT


class CliEmit(_Protocol):
    def __call__(
        self, event: _EventName, sender: str, target: _Any, **kwargs
    ) -> None:
        """Log to EventBus"""


class CliPrint(_Protocol):
    def __call__(self, target: _Any, **kwargs) -> None:
        """Maximally bound CLI call to EventBus"""


class CliEmitter(_Protocol):  # TODO: work out
    """Call to Bus with predefined cli emits"""

    __call__: CliEmit
    panel: Print
    line: Print
    table: Print
    md: Print


class Emitter(_Protocol):
    """Distribute the Emit and Emitter and send the Events"""

    __call__: Emit
    log: LogEmitter
    cli: CliEmitter

    def make(self, **defaults) -> Emitter | LogEmitter | CliEmitter: ...
    def bind(self, event: _EventName, sender: str, **kwargs) -> BoundEmit: ...


class BoundEmit(_Protocol):
    def __call__(self, **kwargs) -> None:
        """Call to bus with predefined Event or Sender"""
