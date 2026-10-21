"""
TAP SPEC

-
                               DependencyLevel.sstcore.port.link[1]
"""

__all__: list[str] = [
    "LinkSpec",
    #
]
from dataclasses import dataclass, replace
from typing import Any, Generic, Protocol, Self, get_protocol_members

from ._define import DocMerger, PortEmit
from ._tap import tap


@dataclass(frozen=True, slots=True)
class LinkSpec:
    # AI: maybe this can stay here when 'merge' and 'emit' are only declared by protocol
    skip: frozenset[type] = frozenset({object, Protocol, Generic})
    on_exit_with_error: bool = True  # TODO: error strategy
    merge: DocMerger = lambda docs: f"merge: {docs}"  # NEXT: same as emit
    emit: PortEmit | None = tap.emit  # IDEA: set default in link.__init__?

    def ignores(self, base: type) -> bool:
        return base in self.skip

    def note(self, *args, sender: Any = None, **kwargs) -> None:
        if self.emit is not None:
            self.emit(*args, sender, **kwargs)

    def derive(self, **kwargs) -> Self:
        return replace(self, **kwargs)

    def surface(self, protocol: type) -> list[str]:
        cls_as_attribute: list[str] = [""]
        return cls_as_attribute + list(get_protocol_members(protocol))
