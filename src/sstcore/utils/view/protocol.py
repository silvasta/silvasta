"""
Provide type information Protocol and support instance checks

- CliDTO: Intended for __cli__ and processed by printer
- LogDTO  Intended for __log__ and processed by logger

"""

from typing import Any, Protocol, runtime_checkable

from .dto import CliDTO, LogDTO


@runtime_checkable
class EventProtocol(Protocol):
    """Structural blueprint for any read-only event payload."""

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
