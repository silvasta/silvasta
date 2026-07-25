"""
Typed, ergonomic facade on top of the EventBus.

- Mirrors common printer + logger patterns
- Provides local functor factories
- Keeps printer focused on rendering only
"""

from dataclasses import dataclass, field
from typing import Any

from ..contract.cli import CliRenderable, PanelDTO, TableDTO
from ..contract.event import CliEvent, EmitFunc, EventName
from ..contract.log import LogDTO, LogSerializable
from .bus import EventBus


# AI: this is a very stable base, I would even like it to use to derive fro LogEmitter
# - issue with frozen data classes, keyword errors, might be problematic
# - emit assigned by Emitter as self in Emitter.make is genious
# - overall the EmitFunc protocol looks promising for LogEmitter (and later CliEmitter)
@dataclass(frozen=True)
class EmitFunctor:
    """Pre-bound, specialized emitter for frequent use cases"""

    emit: EmitFunc
    event_name: EventName
    sender: str
    defaults: dict[str, Any] = field(default_factory=dict)

    def __call__(self, **overrides: Any) -> None:
        self.emit(
            self.event_name, self.sender, **{**self.defaults, **overrides}
        )

    def __repr__(self) -> str:
        return f"EmitFunctor({self.sender!r} → {self.event_name})"


# AI_TASK: create something like LogEmitter but synchronized with the rest
# - no emitter:Emitter but another product of a new Emitter.make factory
# - just use emit:EmitFunc and see it as a more powerful version of EmitFunctor
# used with some overhead for special occurrences, but less bulky than BoundEMitter
@dataclass(frozen=True)
class LogEmitter:
    """Bound sender + default event for chatter."""

    emitter: Emitter
    sender: str
    event: EventName

    # IDEA: how to combine them?

    def __call__(
        self, message: str, *, level: str = "DEBUG", **extra: Any
    ) -> None:
        self.emitter.log(
            self.event, self.sender, message, level=level, **extra
        )

    def info(self, message: str, **extra: Any) -> None:
        self(message, level="INFO", **extra)

    def warning(self, message: str, **extra: Any) -> None:
        self(message, level="WARNING", **extra)

    def error(self, message: str, **extra: Any) -> None:
        self(message, level="ERROR", **extra)

    def success(self, message: str, **extra: Any) -> None:
        self(message, level="SUCCESS", **extra)


x: EmitFunc = LogEmitter.__call__  # AI: type checker happy

# NOTE: usage LogEmitter (will be removed soon)
# # FileUploader.__init__
# em = system.emitter
# self._log = LogEmitter(em, self.sender, DataEvent.TRACE)  # or REMOTE_SYNC
# self._emit_ok = em.make(DataEvent.UPLOAD_COMPLETED, self.sender)
# self._emit_fail = em.make(DataEvent.UPLOAD_FAILED, self.sender)


@dataclass(frozen=True)
class Emitter:  # TESTING: new and untested!
    """Provide unified and simple access to Bus"""

    bus: EventBus

    def __call__(
        self, event_name: EventName, sender: str, **payload: Any
    ) -> None:
        self.bus.emit(event_name, sender, **payload)

    def make(
        self, event_name: EventName, sender: str, **defaults: Any
    ) -> EmitFunctor:
        return EmitFunctor(self, event_name, sender, defaults)

    def make_log(
        self, event_name: EventName, sender: str, **defaults: Any
    ) -> EmitFunctor:
        return EmitFunctor(self, event_name, sender, defaults)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Log shortcuts (testing...)
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def log(
        self,
        event: EventName,
        sender: str,
        message: str,
        *,
        level: str = "INFO",
        **extra: Any,
    ) -> None:
        log_dto = LogDTO(message=message, level=level, extra=extra)
        self(event, sender, log=log_dto)

    # AI: maybe the named logs will be removed, replaced by an internal LogEmitter?
    def info(self, event: EventName, message: str, sender: str, **extra):
        self.log(event, message, sender, "INFO", **extra)

    def warning(self, event: EventName, message: str, sender: str, **extra):
        self.log(event, message, sender, "WARNING", **extra)

    def error(self, event: EventName, message: str, sender: str, **extra):
        self.log(event, message, sender, "ERROR", **extra)  # fixed

    def success(self, event: EventName, message: str, sender: str, **extra):
        self.log(event, message, sender, "SUCCESS", **extra)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### VIEW and CLI
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    def view(
        self,
        event: EventName,
        sender: str,
        target: Any,
        *,
        level: str = "INFO",
    ) -> None:
        payload: dict[str, Any] = {"target": target}

        if isinstance(target, CliRenderable):
            payload["cli"] = target.__cli__()

        if isinstance(target, LogSerializable):
            payload["log"] = target.__log__()

        # TODO: elif?
        elif hasattr(target, "message"):
            payload["log"] = LogDTO(message=str(target), level=level)

        self(event, sender, **payload)

    def panel(self, sender: str, text: str | list[str], **kwargs: Any) -> None:
        # TODO: strong default CliDTO setup
        cli: PanelDTO = PanelDTO.from_call(text=text, **kwargs)
        self(CliEvent.RENDER, sender, cli=cli)

        # TASK: CliEmitter

    def table(self, sender: str, **kwargs: Any) -> None:
        # TODO: strong default CliDTO setup
        self(CliEvent.RENDER, sender, cli=TableDTO.from_call(**kwargs))
