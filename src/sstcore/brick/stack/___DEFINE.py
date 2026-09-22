"""
IMPLEMENT FINAL PROTOCOL HERE

- Temporary until ready to move to proper place

"""

# NEXT: implement

from sstcore.port.calling import Calling

__all__: list[str] = [
    "Stacking",
    "Stack",
]

from collections.abc import Mapping
from typing import Any, Concatenate, Protocol, Self, runtime_checkable


@runtime_checkable
class Stacking(Protocol):
    """Collect Attributes for 1 Mapping for a Stack"""

    @property
    def map(self) -> Mapping: ...


type Call[I, S: Mapping, R] = Calling[Concatenate[I, S], R]


class Stack[I, S: Mapping, R](Protocol):
    """The Executing Core"""

    def __getattr__(self, name: str) -> Stacking:
        """Stack Attributes on top of each other by attribute calls"""

    @property
    def state(self) -> S: ...
    def __call__(self, param=I) -> R: ...

    @classmethod
    def build(
        cls,
        mappings: Mapping[str, Mapping[str, Any]],
        executor: Call[I, S, R],
    ) -> Self: ...
