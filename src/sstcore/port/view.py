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
# TODO: sort the dependencies
# - preferably not depend on event


from typing import Any, Protocol, runtime_checkable

from .event.dto import CliDTO, LogDTO  # TASK: how to remove this?


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
    def __rich__(self) -> Renderable: ...


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


@runtime_checkable
class PydanticModel(Protocol):  # MOVE: but where?
    """Find BaseModels without importing them"""

    def __pydantic_validator__(self): ...
    def model_dump(self) -> dict[str, Any]: ...
