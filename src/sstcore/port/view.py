"""
Define the Shape of Views and their Construction

-
"""

__all__: list[str] = [
    "CliRenderable",
    "Stringable",
    "RichRenderable",
    "ReprRenderable",
    "LogSerializable",
]


from typing import Protocol, runtime_checkable

from .event import CliDTO, LogDTO


@runtime_checkable
class CliRenderable(Protocol):
    def __cli__(self) -> CliDTO: ...


@runtime_checkable
class RichRenderable(Protocol):
    def __rich__(self) -> RichRenderable: ...


@runtime_checkable
class Stringable(Protocol):
    def __str__(self) -> str: ...


@runtime_checkable
class ReprRenderable(Protocol):
    def __repr__(self) -> str: ...


@runtime_checkable
class LogSerializable(Protocol):
    def __log__(self) -> LogDTO: ...


class _FullView(
    CliRenderable,
    RichRenderable,
    Stringable,
    ReprRenderable,
    LogSerializable,
    Protocol,
):
    """Experimental"""
