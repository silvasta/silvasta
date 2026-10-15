"""
Define the Shape of the Event Bus Caller

                              DependencyLevel.sstcore.port.event[2]
"""

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

from ._core import EventBus as _EventBus
from .name import EventName as _EventName

# IDEA: parametrize: -> _Any | None: ?? (e.g. for later on easy EventDTO return)


class Emit(_Protocol):
    def __call__(
        self,
        event: _EventName,
        /,
        # *,#CHECK:
        sender: str,
        **payload,
    ) -> _Any | None:
        """Call to EventBus"""


class Emitter(_Protocol):
    """Distribute the Emit and Emitter and send the Events"""

    @property
    def __call__(self) -> Emit: ...

    bus: _EventBus
    log: LogEmitter
    cli: CliEmitter

    # IDEA: check again, make -> Emitter, log.make -> LogEmitter, cli.make:...
    # - use base with that for all Emitter?? reproducing itself
    def make(self, **defaults) -> Emit | LogEmitter | CliEmitter: ...
    def bind(self, event: _EventName, sender: str, **kwargs) -> BoundEmit: ...


class BoundEmit(_Protocol):
    def __call__(
        self,
        **payload,
    ) -> _Any | None:
        """Call to bus with predefined Event or Sender"""


#  LINE: -- Log -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogEmit(_Protocol):
    def __call__(
        self,
        event: _EventName,
        message: str,
        /,
        sender: str,  # CHECK: keyword argument?
        *,
        level: str = "INFO",
        **extra,
        # **extra: _Mapping[str, _Any], # CHECK: any advantage?
    ) -> _Any | None:
        """Log to EventBus"""


class Log(_Protocol):
    def __call__(
        self,
        message: str,
        /,
        *,
        level: str = "INFO",
        **extra,
    ) -> _Any | None:
        """Maximal bound Log call to EventBus"""


type EventLog = LogEmit | Log


class LogEmitter[Logging: EventLog](_Protocol):
    """Call to Bus with predefined log emits"""

    @property
    def __call__(self) -> LogEmit: ...
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


#  LINE: -- Cli -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CliEmit(_Protocol):
    def __call__(
        self,
        event: _EventName,
        content: _Any,
        /,
        sender: str,
        **kwargs,
    ) -> _Any | None:
        """Render from EventBus"""


class Print(_Protocol):  # LATER: sync with Printer
    def __call__(
        self,
        content: _Any,
        /,
        **kwargs,
    ) -> _Any | None:
        """Maximal bound CLI call to EventBus"""


type CliPrint = CliEmit | Print


class CliEmitter[Printing: CliPrint](_Protocol):
    """Call to Bus with predefined cli emits"""

    # NEXT: work out, with DtoFactory!

    @property
    def __call__(self) -> CliEmit: ...  # CHECK: useful for e.g. Printer?
    @property
    def panel(self) -> Printing: ...
    @property
    def md(self) -> Printing: ...
    @property
    def line(self) -> Printing: ...
    @property
    def table(self) -> Printing: ...
