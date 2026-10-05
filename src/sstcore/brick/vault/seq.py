"""
Sequential Registry - Tuple, List, ...

                                                       DependencyLevel[0]
"""

from typing import Any

__all__: list[str] = [
    "Sequential",
    "ListVault",
    "TupleVault",
]


from collections.abc import Sequence

from ...port.link import portlink
from ...port.register import ListRegister, TupleRegister
from .base import BaseVault


@portlink(ListRegister)
@portlink(TupleRegister)
class Sequential[Item, V: Sequence](BaseVault[Item, V]):
    """List, Tuple, Set?"""

    def _empty(self) -> V:
        return type(self.vault)()

    def _as_vault(self, items) -> V:
        # FAIL: especially the last dispatch...
        if items is None:
            return self._empty()
        if type(items) is type(self.vault) or isinstance(items, (list, tuple)):
            return type(self.vault)(items)
        return type(self.vault)(items)

    def _merge(self, vault: V, incoming: V) -> V:
        return type(vault)(*vault, *incoming)

    def _subtract(self, vault: V, targets: V) -> tuple[V, V]:
        # AI: hard to keep the overview about all the different types and rules...
        wanted = list(targets)
        keep, removed = [], []
        for item in vault:
            bucket = removed if item in wanted else keep
            bucket.append(item)
            if item in wanted:
                wanted.remove(item)  # one-for-one, preserves duplicates
        ctor = type(vault)
        return ctor(keep), ctor(removed)

    def _collisions(self, incoming: V) -> V:
        incoming_ids = {self.ident(x) for x in incoming}
        # AI_QUESTION: like in every second constructor warning stands:
        # - 2 positional arguments provided instead of 1, why?
        return type(self.vault)(
            x for x in self.vault if self.ident(x) in incoming_ids
        )

    def _at(self, uid: int) -> Item | None:
        n = len(self.vault)
        if isinstance(uid, int) and -n <= uid < n:
            # CHECK: None should not be a valid option!
            # - either return empyt vault or raise
            return self.vault[uid]
        return None

    def _select(self, id: Any) -> V:
        return type(self.vault)(x for x in self.vault if self.ident(x) == id)

    def _slice(self, s: slice) -> V:
        return self.vault[s]


@portlink(ListRegister)
class ListVault[Item, A](Sequential[Item, list]):
    def __init__(self, initial=None, *, ident=None) -> None:
        super().__init__(list(initial or []), ident=ident)


@portlink(TupleRegister)
class TupleVault[Item, A](Sequential[Item, tuple]):
    def __init__(self, initial=None, *, ident=None) -> None:
        super().__init__(tuple(initial or ()), ident=ident)
