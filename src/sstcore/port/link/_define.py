"""
Setup the Protocols that guide the Behaviour of the Implementations

- Including the LinkSpec config (it is lost otherwise)

                               DependencyLevel.sstcore.port.link[1]
"""

__all__: list[str] = [
    "PortLinker",
    "DocMerger",
    "PortEmit",
    "Reflecting",
    "Injecting",
    "Collecting",
]

from typing import Any, Protocol

from ._model import Docs, PortLinks


class PortLinker[C, P](Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


class PortEmit[**P](Protocol):
    def __call__(self, *args, sender: Any = None, **kwargs) -> None:
        """Define the message structure of port internal events"""


class DocMerger(Protocol):  # IDEA: Merging? only if as well operator
    def __call__(self, docs: Docs) -> str:
        """Format and Render Protocol and Implementation docstrings"""


class Reflecting(Protocol):
    def __call__(self, target: Any, attr: str, /) -> Any:
        """Extract the attribute value from the target"""


class Injecting(Protocol):
    def __call__(self, target: Any, value: Any, /, attr: str) -> str:
        """Attach the new attribute value into the target"""


class Collecting(Protocol):
    def __call__(self, port: type, plug: type, attr: str, /) -> PortLinks:
        """Harvest data in both sides MRO pipeline"""
