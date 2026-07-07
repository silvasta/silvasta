"""
Provide type information (and checks) for classes

- CliDto for __cli__ and printer
- LogDto for __log__ and logger
"""

from typing import Protocol, runtime_checkable

from .dto import CliDTO, LogDTO


# AI_QUESTION: about: @runtime_checkable, gain or pain?
# at least PanelDTO worked in quick script test
@runtime_checkable
class CliRenderable(Protocol):
    def __cli__(self) -> CliDTO: ...


@runtime_checkable
class LogSerializable(Protocol):  # TODO: check name
    def __log__(self) -> LogDTO: ...
