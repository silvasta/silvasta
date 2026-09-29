"""
config

- temporary module
"""

import typing as _t

from .._field import FixTypeField


class LinkSpec:  # LATER: make it separable, formatter, portlink-app, ...
    name = FixTypeField[str](types=str)
    skip = FixTypeField[frozenset[type]](types=frozenset)
    on_exit_with_error: bool = True

    def __init__(self, *, skip: frozenset[type]) -> None:
        self.skip: frozenset[type] = skip

    def ignores(self, base: type) -> bool:
        return base in self.skip


_SKIP: frozenset[type] = frozenset({object, _t.Protocol, _t.Generic})

spec = LinkSpec(skip=_SKIP)
