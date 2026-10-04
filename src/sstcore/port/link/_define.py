"""
Setup the Protocols that guide the Behaviour of the Implementations

- Including the LinkSpec config (it is lost otherwise)

                               DependencyLevel.sstcore.port.link[1]
"""

__all__: list[str] = [
    "LinkSpec",
    #
    "PortLinker",
    "DocMerger",
    "PortEmit",
    "Reflecting",
    "Injecting",
    "Collecting",
]


from dataclasses import dataclass, replace
from typing import Any, Generic, Protocol, Self, get_protocol_members

from ._model import Docs, PortLinks


class PortLinker[C, P](Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


class DocMerger(Protocol):  # IDEA: Merging? only if as well operator
    def __call__(self, docs: Docs) -> str:
        """Format and Render Protocol and Implementation docstrings"""


class PortEmit[**P](Protocol):
    def __call__(self, *arg: P.args, **kwarg: P.kwargs) -> None: ...


class Reflecting(Protocol):
    def __call__(self, target: Any, attr: str, /) -> Any:
        """Extract the attribute value from the target"""


class Injecting(Protocol):
    def __call__(self, target: Any, value: Any, /, attr: str) -> str:
        """Attach the new attribute value into the target"""


class Collecting(Protocol):
    def __call__(self, port: type, plug: type, attr: str, /) -> PortLinks:
        """Harvest data in both sides MRO pipeline"""


@dataclass(frozen=True, slots=True)
class LinkSpec:
    skip: frozenset[type] = frozenset({object, Protocol, Generic})
    on_exit_with_error: bool = True  # TODO:
    merge: DocMerger = lambda docs: f"merge: {docs}"
    emit: PortEmit | None = None

    def ignores(self, base: type) -> bool:
        return base in self.skip

    def note(self, event: Any) -> None:
        if self.emit is not None:
            self.emit(event)

    def derive(self, **kwargs) -> Self:
        return replace(self, **kwargs)

    def surface(self, protocol: type) -> list[str]:
        cls_as_attribute: list[str] = [""]
        return cls_as_attribute + list(get_protocol_members(protocol))
