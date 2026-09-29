"""
config

- temporary module
"""

import typing as _t
from dataclasses import dataclass as _dataclass
from dataclasses import replace as _replace

from .define import DocMerger, PortEmit
from .process import merger


class LinkEvent(_t.NamedTuple):
    kind: _t.Literal["missing", "linked"]
    protocol: type
    cls: type
    attr: str = ""


@_dataclass(frozen=True, slots=True)
class LinkSpec:
    skip: frozenset[type] = frozenset({object, _t.Protocol, _t.Generic})
    on_exit_with_error: bool = True  # TODO:
    merge: DocMerger = merger
    emit: PortEmit | None = None

    def ignores(self, base: type) -> bool:
        return base in self.skip

    def note(self, event: LinkEvent) -> None:
        if self.emit is not None:
            self.emit(event)

    def derive(self, **kwargs) -> _t.Self:
        return _replace(self, **kwargs)

    def surface(self, protocol: type) -> list[str]:
        cls_as_attribute: list[str] = [""]
        return cls_as_attribute + list(_t.get_protocol_members(protocol))


spec = LinkSpec()
