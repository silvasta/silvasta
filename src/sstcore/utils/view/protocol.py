"""
Provide type information Protocol and support instance checks

- CliDTO: Intended for __cli__ and processed by printer
- LogDTO  Intended for __log__ and processed by logger

"""

from typing import Any, Protocol, runtime_checkable

from rich.console import ConsoleRenderable, RichCast

from .dto import CliDTO, LogDTO


@runtime_checkable
class EventProtocol(Protocol):
    """Show the handler in utils how an event looks"""

    @property
    def name(self) -> str: ...

    @property
    def sender(self) -> str: ...

    @property
    def payload(self) -> dict[str, Any]: ...


@runtime_checkable
class CliRenderable(Protocol):
    def __cli__(self) -> CliDTO: ...


@runtime_checkable
class LogSerializable(Protocol):
    def __log__(self) -> LogDTO: ...


type RichRenderable = ConsoleRenderable | RichCast


class MixinSentinel:
    """Imitate a Mixin and replace None"""

    def __cli__(self) -> CliDTO:
        raise NotImplementedError

    def __log__(self) -> LogDTO:
        raise NotImplementedError

    def __rich__(self) -> RichRenderable:
        raise NotImplementedError
