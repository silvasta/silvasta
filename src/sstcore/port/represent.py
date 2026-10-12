"""
Define the Shape of Views and what they Represent.

- temporary refactored...
                                    DependencyLevel.sstcore.port[8]
"""

# NEXT: Split!!

__all__: list[str] = [
    "SstView",
    "SstViewType",
    "CliSerializable",
    "LogSerializable",
    "LogStringable",
    "Stringable",
    "RichView",
]
from typing import Protocol as _Protocol
from typing import runtime_checkable as _runtime_checkable

from .calling import Richable as _Richable
from .event import CliDTO, LogDTO

type SstViewType = (
    CliSerializable | LogSerializable | LogStringable | Stringable | RichView
)

type CliRenderable = CliSerializable | str | _Richable  # CHECK: __log__??


class SstView(_Protocol):  # TODO:
    """Here comes the final result"""


class SstPropView(_Protocol):
    """Combine all frequently used Views"""

    def __cli__(self) -> CliSerializable: ...
    def __log__(self) -> LogSerializable: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __rich__(self) -> _Richable: ...


class SstFullView(_Protocol):
    def __cli__(self) -> CliDTO:
        """Snapshot the Target for Visualization"""

    def __log__(self) -> LogDTO:
        """Messaage the Event for Traceability"""

    def __repr__(self) -> str:
        """Concate the Event info to long String"""

    def __str__(self) -> str:
        """Just provide a Name Identifier"""

    def __rich__(self) -> _Richable:
        """Provide a colorized Name Identifier"""


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_runtime_checkable
class CliSerializable(_Protocol):
    def __cli__(self) -> CliDTO:
        """Snapshot the Target for Visualization"""


@_runtime_checkable
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
