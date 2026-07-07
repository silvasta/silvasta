"""
Provide type information (and checks) for classes

- CliDto for __cli__ and printer
- LogDto for __log__ and logger
"""

from typing import Protocol, runtime_checkable

from .dto import CliDTO, LogDTO


@runtime_checkable
class CliRenderable(Protocol):
    def __cli__(self) -> CliDTO: ...


@runtime_checkable
class LogSerializable(Protocol):
    def __log__(self) -> LogDTO: ...
