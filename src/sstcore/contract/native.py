"""Define Contracts on Native Python types"""

__all__: list[str] = [
    "Stringable",
    "ReprRenderable",
]
from typing import Protocol, runtime_checkable

# TASK: compare with LogSerializable, CliRenderable, unite!


@runtime_checkable
class Stringable(Protocol):
    def __str__(self) -> str: ...


@runtime_checkable
class ReprRenderable(Protocol):
    def __repr__(self) -> str: ...
