"""
Define the Shape of Views and what they Represent.

- temporary refactored...
                                                 DependencyLevel[5]
                                                           event(4)
"""

# NEXT: LEVEL
#
__all__: list[str] = [
    "LogSerializable",
    "CliRenderable",
]
from typing import Protocol as _Protocol

from .calling import Richable as _Richable

# TODO: check private, assemble Richable?
from .event import CliDTO, LogDTO


class CliRenderable(_Protocol):
    def __cli__(self) -> CliDTO:
        """Snapshot the Target for Visualization"""


class LogSerializable(_Protocol):
    def __log__(self) -> LogDTO:
        """Messaage the Event for Traceability"""


class LogStringable(_Protocol):
    def __repr__(self) -> str:
        """Concate the Event info to long String"""


class Stringable(_Protocol):
    def __str__(self) -> str:
        """Just provide a Name Identifier"""


class RichView(_Protocol):
    def __rich__(self) -> _Richable:
        """Provide a colorized Name Identifier"""


type Renderable = CliRenderable | str | _Richable
