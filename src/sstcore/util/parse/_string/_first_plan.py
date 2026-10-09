"""
The View Table

-
"""

__all__: list[str] = [
    # "",
]

# TASK: build execution for brick.format.tstring

from datetime import datetime
from typing import Any, Protocol

from msgspec import Struct

from ....port.calling import Stringable


class Tstring(Struct):
    tstring: str
    normalized: str
    written: str
    final: str
    units: list[Any] = []
    time: datetime = datetime.now()  # NOTE: is this fine on msgspec?


class TstringInternal(Protocol):
    def __call__(self, extracted: object) -> Stringable:
        """Path from extracted bracket object until boarder"""


class ReadyToRender(Struct):
    text: str
    units: list[Any] = []
    colorset: Any = None
    time: datetime = datetime.now()  # NOTE: is this fine on msgspec?
