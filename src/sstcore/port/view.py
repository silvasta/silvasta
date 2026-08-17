"""
Define the Shape of Views and what they Represent.

-
"""

__all__: list[str] = [
    "CliRenderable",  # __cli__
    "LogSerializable",  # __log__
    "Reprable",  # __repr__
    "Stringable",  # __str__
    "RichRenderable",  # __rich__
    #
    "FullView",
    "Renderable",
]


from typing import Protocol, runtime_checkable

from .event import CliDTO, LogDTO


@runtime_checkable
class CliRenderable(Protocol):
    def __cli__(self) -> CliDTO: ...


@runtime_checkable
class LogSerializable(Protocol):
    def __log__(self) -> LogDTO: ...


@runtime_checkable
class Reprable(Protocol):
    def __repr__(self) -> str: ...


@runtime_checkable
class Stringable(Protocol):
    def __str__(self) -> str: ...


@runtime_checkable
class RichRenderable(Protocol):
    def __rich__(self) -> RichRenderable: ...


@runtime_checkable
class FullView(
    CliRenderable,
    LogSerializable,
    Reprable,
    Stringable,
    RichRenderable,
    Protocol,
):
    """Type the view when all bricks are set"""


type Renderable = RichRenderable | _RichConsolable | CliRenderable | str


class _RichConsolable(Protocol):
    def __rich_console__(self):
        """Just extend the Renderable type"""
