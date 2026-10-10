"""
Sequential Registry - Tuple, List, ...

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "Sequential",
    "ListVault",
    "TupleVault",
]


from collections.abc import Iterable, Iterator, Sequence
from typing import Any

from ...port.link import portlink
from ...port.register import ListRegister, TupleRegister
from ...port.register import registry_types as _reg
from ._base import BaseVault


class Sequential[Item, V: Sequence](BaseVault[Item, V]):
    """Implement the Contract"""

    def _ctor(self, items: Iterable[Item], /) -> V:
        raise NotImplementedError(items)

    def _empty(self) -> V:
        return self._ctor(())

    def _as_vault(self, data: Any) -> V:
        if data is None:
            return self._empty()
        if isinstance(data, (str, bytes)):
            return self._ctor((self._normalize(data),))
        if isinstance(data, Iterable):
            return self._ctor(self._normalize(x) for x in data)
        return self._ctor((self._normalize(data),))

    def _merge(self, vault: V, incoming: V) -> V:
        return self._ctor([*vault, *incoming])

    def _subtract(self, vault: V, targets: V) -> tuple[V, V]:
        wanted: list[Any] = [self._item_id(x) for x in targets]
        keep: list[Item] = []
        removed: list[Item] = []
        for item in vault:
            iid: Any = self._item_id(item)
            if iid in wanted:
                removed.append(item)
                wanted.remove(iid)
            else:
                keep.append(item)
        return self._ctor(keep), self._ctor(removed)

    def _collisions(self, incoming: V) -> V:
        ids: set[Item] = {self._item_id(x) for x in incoming}
        return self._ctor(x for x in self.vault if self._item_id(x) in ids)

    def _iter_items(self) -> Iterator[Item]:
        yield from self.vault

    def _index_item(self, idx: int) -> Item:
        return self.vault[self._normalize_index(idx)]

    def _index_put(self, idx: int, item: Item) -> None:
        items: list[Item] = list(self.vault)
        items[self._normalize_index(idx)] = item
        self.vault: V = self._ctor(items)

    def _key_item(self, key: str) -> Item:
        found: list[Item] = [x for x in self if self._item_id(x) == key]
        if len(found) != 1:
            raise KeyError(key)
        return found[0]

    def _box_key(self, key: str) -> V:
        return self._ctor(x for x in self if self._item_id(x) == key)

    def _slice(self, s: slice) -> V:
        return self._ctor(self.vault[s])

    def _slice_put(self, s: slice, value: Any) -> None:
        items: list[Item] = list(self._iter_items())
        items[s] = list(self._as_vault(value))
        self.vault: V = self._ctor(items)

    def _where(self, fn: _reg.Predicate[Item]) -> V:
        return self._ctor(x for x in self._iter_items() if fn(x))


@portlink(ListRegister)
class ListVault[Item](Sequential[Item, list[Item]]):
    def _ctor(self, items: Iterable[Item]) -> list[Item]:
        return list(items)


@portlink(TupleRegister)
class TupleVault[Item](Sequential[Item, tuple[Item, ...]]):
    def _ctor(self, items: Iterable[Item]) -> tuple[Item, ...]:
        return tuple(items)
