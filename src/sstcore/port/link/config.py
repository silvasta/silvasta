"""
config

- temporary module
"""

import typing as _t
from dataclasses import dataclass

from .define import DocMerger, PortEmit
from .process import merger


@dataclass(frozen=True, slots=True)
class LinkSpec:
    skip: frozenset[type] = frozenset({object, _t.Protocol, _t.Generic})
    on_exit_with_error: bool = True  # TODO:
    merge: DocMerger = merger
    emit: PortEmit | None = None

    def ignores(self, base: type) -> bool:
        return base in self.skip


spec = LinkSpec()
