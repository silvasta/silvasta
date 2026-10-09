"""
Define the Shape of Views and what they Represent.

- temporary refactored...
                                    DependencyLevel.sstcore.port[8]
"""

# NEXT: Split!!

__all__: list[str] = [
    "SstView",
    "SstViewType",
    "LogSerializable",  # RENAME: LogSerialize??
    "CliSerializable",  # RENAME: CliSerialize??
]
from typing import Protocol as _Protocol

from .calling import Richable as _Richable
from .event import CliDTO, LogDTO  # TODO: check internal pipeline, dependency

type SstViewType = (
    CliSerializable | LogSerializable | LogStringable | Stringable | RichView
)

type CliRenderable = CliSerializable | str | _Richable  # CHECK: __log__??


class SstView(_Protocol):  # TODO:
    """Here comes the final result"""


class SstPropView(_Protocol):
    """Combine all frequently used Views"""

    @property
    def __cli__(self) -> CliSerializable: ...
    @property
    def __log__(self) -> LogSerializable: ...
    @property
    def __repr__(self) -> LogStringable: ...
    @property
    def __str__(self) -> Stringable: ...
    @property
    def __rich__(self) -> RichView: ...


class SstShortView(_Protocol):
    """Combine all frequently used Views"""

    __cli__: CliSerializable
    __log__: LogSerializable
    __repr__: LogStringable
    __str__: Stringable
    __rich__: RichView


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


class CliSerializable(_Protocol):
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
