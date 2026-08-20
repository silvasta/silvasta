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

# TODO: sort the dependencies
# - preferably not depend on event
from .event.dto import CliDTO, LogDTO

# IDEA: split, refactor, remove entire view here?
# - it is very amazing as 1 overview over all implementations
# - but it is nothing more than a nice portrait or similar
# - the value for the code goes to 0
# - the representability and documentation will slightly loose
# overall the implementations show enoug to anyone
# who is able to think a little bit how it works
# and don't need the perfect view of the views below
# - maybe I place them in brick.view docstring


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
