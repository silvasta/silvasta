"""
Sequential Registry - Tuple, List, ...

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "Sequential",
    "ListVault",
    "TupleVault",
]


from collections.abc import Iterator, Sequence
from typing import Any

from ...port.link import portlink
from ...port.register import ListRegister, TupleRegister
from ...port.register import registry_types as _reg
from ._base import BaseVault


@portlink(ListRegister)
@portlink(TupleRegister)
class Sequential[Item, V: _reg.Seq[Item]](BaseVault[Item, V]):
    def _ctor(self, items: _reg.Iter[Item]) -> V:
        raise NotImplementedError(items)

    def _empty(self) -> V:
        return self._ctor(())

    def _as_vault(self, data: Any) -> V:
        if data is None:
            return self._empty()
        if isinstance(data, (str, bytes)):
            return self._ctor((data,))
        if isinstance(data, Sequence):
            return self._ctor(data)
        return self._ctor((data,))

    def _merge(self, vault: V, incoming: V) -> V:
        return self._ctor([*vault, *incoming])

    def _subtract(self, vault: V, targets: V) -> tuple[V, V]:
        wanted = [self._item_id(x) for x in targets]
        keep, removed = [], []
        for item in vault:
            iid = self._item_id(item)
            if iid in wanted:
                removed.append(item)
                wanted.remove(iid)
            else:
                keep.append(item)
        return self._ctor(keep), self._ctor(removed)

    def _collisions(self, incoming: V) -> V:
        ids: list[Item] = [self._item_id(x) for x in incoming]
        return self._ctor(x for x in self.vault if self._item_id(x) in ids)

    def _iter_items(self) -> Iterator[Item]:
        yield from self.vault

    def _index_item(self, idx: int) -> Item:
        return self.vault[self._normalize_index(idx)]

    def _index_put(self, idx: int, item: Item) -> None:
        items = list(self.vault)
        items[self._normalize_index(idx)] = item
        self.vault = self._ctor(items)

    def _key_item(self, key: str) -> Item:
        found = [x for x in self.vault if self._item_id(x) == key]
        if len(found) != 1:
            raise KeyError(key)
        return found[0]

    def _box_key(self, key: str) -> V:
        return self._ctor(x for x in self.vault if self._item_id(x) == key)

    def _slice(self, s: slice) -> V:
        return self._ctor(self.vault[s])


class ListVault[Item](Sequential[Item, list[Item]]):
    def _ctor(self, items: _reg.Iter[Item]) -> list[Item]:
        return list(items)


class TupleVault[Item](Sequential[Item, tuple[Item, ...]]):
    def _ctor(self, items: _reg.Iter[Item]) -> tuple[Item, ...]:
        return tuple(items)
