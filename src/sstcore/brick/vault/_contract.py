"""
Basic Definitions and Responsibilities

-
"""

__all__: list[str] = [
    "VaultContract",
]


from collections.abc import Iterator
from typing import Any

from ...port.register import registry_types as _r


class VaultContract[Item, V: _r.Vault]:
    """
    Set the direction and prepare the main processes (no abc here!)

      - Note: the docs here are important and stacked through mro
    """

    vault: V
    ident: _r.Ident[Item]

    def _empty(self) -> V:
        """Create an empty backing container"""
        raise NotImplementedError

    def _as_vault(self, data: Any, /) -> V:
        """Convert arbitrary input into a conforming vault container"""
        raise NotImplementedError(data)

    def _merge(self, vault: V, incoming: V, /) -> V:
        """Combine two vault containers into a single container"""
        raise NotImplementedError(vault, incoming)

    def _subtract(self, vault: V, targets: V, /) -> tuple[V, V]:
        """Split a vault container into kept and removed subsets"""
        raise NotImplementedError(vault, targets)

    def _collisions(self, incoming: V) -> V:
        """Find elements in incoming that conflict with current contents"""
        raise NotImplementedError(incoming)

    def _iter_items(self) -> Iterator[Item]:
        """Yield each item stored in the backing container"""
        raise NotImplementedError

    def _index_item(self, idx: int) -> Item:
        """Retrieve the item at the specified integer index"""
        raise NotImplementedError(idx)

    def _index_put(self, idx: int, item: Item) -> None:
        """Store an item at the specified integer index"""
        raise NotImplementedError(idx, item)

    def _key_item(self, key: str) -> Item:
        """Retrieve the unique item associated with a key identifier"""
        raise NotImplementedError(key)

    def _key_put(self, key: str, item: Item) -> None:
        """Store an item under the specified key identifier"""
        raise NotImplementedError(key, item)

    def _box_index(self, idx: int) -> V:
        """Return the item at the specified index wrapped in a vault"""
        raise NotImplementedError(idx)

    def _box_key(self, key: str) -> V:
        """Return the item matching the key wrapped in a vault"""
        raise NotImplementedError(key)

    def _slice(self, s: slice) -> V:
        """Extract a sub-vault bounded by the given slice"""
        raise NotImplementedError(s)

    def _slice_put(self, s: slice, value: Any) -> None:
        """Assign values across the range defined by a slice"""
        raise NotImplementedError(s, value)

    def _where(self, fn: _r.Predicate[Item]) -> V:
        """Filter items satisfying a predicate into a new vault"""
        raise NotImplementedError(fn)

    def _replace_where(self, fn: _r.Predicate[Item], item: Item) -> None:
        """Replace all items matching a predicate with a replacement item"""
        raise NotImplementedError(fn, item)

    def _gather(self, keys: tuple[Any,]) -> V:
        """Collect multiple items by selector tuple into a new vault"""
        raise NotImplementedError(keys)

    def _normalize(self, value: Any) -> Item:
        """Cast or validate incoming data into a canonical item instance"""
        return value

    def _item_id(self, item: Item, /) -> Any:
        """Compute the unique identity key for an item"""
        return self.ident(item)

    def _normalize_index(self, idx: int) -> int:
        """Resolve negative offsets and assert positive index bounds"""
        n: int = len(self.vault)
        if idx < 0:
            idx += n
        if not 0 <= idx < n:
            raise IndexError(idx)
        return idx
