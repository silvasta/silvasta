"""
Provide type information Protocol and support instance checks

- EventProtocol: define sstcore.system.bus.Event for sstcore.utils

"""

__all__: list[str] = [
    "EventProtocol",
]

from typing import Any, Protocol, runtime_checkable

from rich.console import ConsoleRenderable, RichCast


@runtime_checkable
class EventProtocol(Protocol):
    """Show the handler in utils how an event looks"""

    @property
    def name(self) -> str: ...

    @property
    def sender(self) -> str: ...

    @property
    def payload(self) -> dict[str, Any]: ...


# WARN: unrelated definition...
type RichRenderable = ConsoleRenderable | RichCast
