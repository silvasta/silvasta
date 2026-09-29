"""
Setup the Protocols that guide the Behaviour of the Implementations

- Including the LinkSpec config (it is lost otherwise)

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


import typing as _t
from dataclasses import dataclass as _dataclass
from dataclasses import replace as _replace

from ._model import Docs, PortLinks


class PortLinker[C, P](_t.Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


class DocMerger(_t.Protocol):  # IDEA: Merging? only if as well operator
    def __call__(self, docs: Docs) -> str:
        """Format and Render Protocol and Implementation docstrings"""


class PortEmit[**P](_t.Protocol):
    def __call__(self, *arg: P.args, **kwarg: P.kwargs) -> None: ...


class Reflecting(_t.Protocol):
    def __call__(self, target: _t.Any, attr: str, /) -> _t.Any:
        """Extract the attribute value from the target"""


class Injecting(_t.Protocol):
    def __call__(self, target: _t.Any, value: _t.Any, /, attr: str) -> str:
        """Attach the new attribute value into the target"""


class Collecting(_t.Protocol):
    def __call__(self, port: type, plug: type, attr: str, /) -> PortLinks:
        """Harvest data in both sides MRO pipeline"""


@_dataclass(frozen=True, slots=True)
class LinkSpec:
    skip: frozenset[type] = frozenset({object, _t.Protocol, _t.Generic})
    on_exit_with_error: bool = True  # TODO:
    merge: DocMerger = lambda docs: f"merge: {docs}"
    emit: PortEmit | None = None

    def ignores(self, base: type) -> bool:
        return base in self.skip

    def note(self, event: _t.Any) -> None:
        if self.emit is not None:
            self.emit(event)

    def derive(self, **kwargs) -> _t.Self:
        return _replace(self, **kwargs)

    def surface(self, protocol: type) -> list[str]:
        cls_as_attribute: list[str] = [""]
        return cls_as_attribute + list(_t.get_protocol_members(protocol))
