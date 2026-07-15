"""Define Contracts on Native Python types"""

__all__: list[str] = [
    "RichRenderable",
    "RichProtocol",
]

from typing import Protocol, runtime_checkable

from rich.console import ConsoleRenderable, RichCast


@runtime_checkable
class RichProtocol(Protocol):
    def __rich__(self) -> RichRenderable: ...


type RichRenderable = ConsoleRenderable | RichCast
