"""
Basic Definitions and Responsibilities

- Name:
  - AbstractVault
  - InitialVault
  - TemplateVault
  - VaultContract
  - VaultTemplate
"""

__all__: list[str] = [
    "AbstractVault",
]


from collections.abc import Iterator
from typing import Any

from ...port.register import registry_types as _rtype


class AbstractVault[Item, V: _rtype.Vault]:
    vault: V
    ident: _rtype.Ident[Item]

    def _empty(self) -> V:
        raise NotImplementedError

    def _as_vault(self, data: Any, /) -> V:
        raise NotImplementedError

    def _merge(self, vault: V, incoming: V) -> V:
        raise NotImplementedError

    def _subtract(self, vault: V, targets: V) -> tuple[V, V]:
        raise NotImplementedError

    def _collisions(self, incoming: V) -> V:
        raise NotImplementedError

    def _iter_items(self) -> Iterator[Item]:
        raise NotImplementedError

    def _index_item(self, idx: int) -> Item:
        raise NotImplementedError

    def _index_put(self, idx: int, item: Item) -> None:
        raise NotImplementedError

    def _key_item(self, key: str) -> Item:
        raise NotImplementedError

    def _key_put(self, key: str, item: Item) -> None:
        raise NotImplementedError

    def _box_index(self, idx: int) -> V:
        raise NotImplementedError

    def _box_key(self, key: str) -> V:
        raise NotImplementedError

    def _slice(self, s: slice) -> V:
        raise NotImplementedError

    def _slice_put(self, s: slice, value: Any) -> None:
        raise NotImplementedError

    def _where(self, fn: _rtype.Predicate[Item]) -> V:
        raise NotImplementedError

    def _replace_where(self, fn: _rtype.Predicate[Item], item: Item) -> None:
        raise NotImplementedError

    def _gather(self, keys: tuple[Any, ...]) -> V:
        raise NotImplementedError

    def _normalize(self, value: Any) -> Item:
        return value

    def _item_id(self, item: Item) -> Any:
        # REMOVE: ? directly call ident, ident=None not allowed
        return self.ident(item)

    def _normalize_index(self, idx: int) -> int:
        n = len(self.vault)
        if idx < 0:
            idx += n
        if not 0 <= idx < n:
            raise IndexError(idx)
        return idx
