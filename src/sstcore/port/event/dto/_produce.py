"""
Orchestrate the EventDTO Production Facilities

-
"""

__all__: list[str] = [
    "DtoFactory",
    "CliDtoCreator",
]


from typing import Protocol, runtime_checkable

from ._base import EventDTO
from ._cli import CliDTO


class DtoFactory(Protocol):  # NEXT:
    def __call__(self, cls: type) -> EventDTO: ...


@runtime_checkable
class CliDtoCreator(Protocol):  # NEXT:
    def __call__(self, cls: type) -> CliDTO: ...
