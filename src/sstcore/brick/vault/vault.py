"""
Define the Shape of the Core Registry

- 1 Interface for Any type of Vaults -> enable independent data handling

                                                 DependencyLevel[2]
                                                        - filter(1)
"""

from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any, Self, overload

from annotated_types import Predicate

# NEXT:
type _Vaults = list | tuple | dict
type Vaults = Sequence | Mapping


class Vault[Item]:
    def __init__(self, items: list[Item] | None = None) -> None:
        self._items: list[Item] = list(items or [])

    # Overload 1: Exact integer position -> single Item
    @overload
    def __getitem__(self, key: int) -> Item: ...

    # Overload 2: Slices, callables, or multi-key tuples -> new Vault
    @overload
    def __getitem__(
        self, key: slice | Predicate | tuple[Any, ...]
    ) -> Vault: ...

    # Overload 3: Unique string key -> single Item
    @overload
    def __getitem__(self, key: str) -> Item: ...

    def __getitem__(self, key: Any) -> Any:
        match key:
            case int() as idx:
                return self._items[idx]

            case slice() as s:
                return Vault(self._items[s])

            case str() as k:
                for item in self._items:
                    if item[0] == k:
                        return item
                raise KeyError(k)

            case tuple() as multi_keys:
                # vault["id1", "id2", 0] -> resolves multiple selectors
                matched: list[Item] = []
                for sub_key in multi_keys:
                    res = self[sub_key]
                    if isinstance(res, Vault):
                        matched.extend(res._items)
                    else:
                        matched.append(res)
                return Vault(matched)

            case fn if callable(fn):
                return Vault([item for item in self._items if fn(item)])

            case _:
                raise TypeError(
                    f"Unsupported selector type: {type(key).__name__}"
                )

    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    def __setitem__(self, key: Any, value: Any) -> None:
        match key:
            # 1. Positional overwrite
            case int() as idx:
                self._items[idx] = self._normalize_item(value)

            # 2. Slice assignment (Python standard list slice behavior)
            case slice() as s:
                self._items[s] = [self._normalize_item(v) for v in value]

            # 3. Key-based replacement or append
            case str() as k:
                norm_val = self._normalize_item(value, default_key=k)
                for idx, (existing_k, _) in enumerate(self._items):
                    if existing_k == k:
                        self._items[idx] = norm_val
                        return
                self._items.append(norm_val)

            # 4. Predicate batch update (e.g. vault[fn] = new_value)
            case fn if callable(fn):
                for idx, item in enumerate(self._items):
                    if fn(item):
                        # If a function is passed as value, compute replacement dynamically
                        if callable(value):
                            self._items[idx] = self._normalize_item(
                                value(item)
                            )
                        else:
                            self._items[idx] = self._normalize_item(value)

            # 5. Multi-key batch assignment: vault["a", "b"] = [item1, item2]
            case tuple() as multi_keys:
                values = list(value)
                if len(multi_keys) != len(values):
                    raise ValueError(
                        f"Cannot unpack {len(values)} values into {len(multi_keys)} selectors"
                    )
                for sub_key, sub_val in zip(multi_keys, values, strict=True):
                    self[sub_key] = sub_val

            case _:
                raise TypeError(f"Unsupported selector: {type(key).__name__}")

    @staticmethod
    def _normalize_item(val: Any, default_key: str = "") -> Item:
        """Coerces raw values or 2-tuples into a valid Item."""
        if (
            isinstance(val, tuple)
            and len(val) == 2
            and isinstance(val[0], str)
        ):
            return val
        return (default_key, val)


type Selector[A] = A | Iterable[A]


def _resolve_identifiers[A](selector: Selector[A]) -> list[A]:
    # EXTRACT:
    if isinstance(selector, (str, bytes)):  # Guard against iterating strings
        return [selector]  # type: ignore
    if isinstance(selector, Iterable):
        return list(selector)
    return [selector]


class Vault2[A, Item]:
    def find(self, id: Selector[A]) -> Self:
        """Accepts a single id, a list of ids, or a tuple of ids."""
        target_ids = set(_resolve_identifiers(id))
        return Vault([item for item in self._items if item[0] in target_ids])

    def clear(self, id: Selector[A] | None = None) -> Vault:
        """Remove matching elements, or clear all if None."""
        if id is None:
            removed = self._items[:]
            self._items.clear()
            return Vault(removed)

        target_ids = set(_resolve_identifiers(id))
        retained: list[Item] = []
        removed: list[Item] = []
        for item in self._items:
            (removed if item[0] in target_ids else retained).append(item)
        self._items = retained
        return Vault(removed)


class V1[Item, Vault: Vaults, U, A: Any]:
    """Provide initial Setup"""

    def _clear_all(self) -> None:
        raise NotImplementedError

    def _slice_action(self, s: slice) -> Any:
        raise NotImplementedError

    def _str_action(self, k: str) -> Any:
        raise NotImplementedError

    def _item_action(self, target: Item) -> Any:
        raise NotImplementedError

    def _int_action(self, i: int) -> Item | None:
        raise NotImplementedError

    def _sanitize(self, result: Vault | Item | None) -> Vault:
        raise NotImplementedError

    def _remove(self, targets: Vault) -> Vault:
        """Return all removed"""
        raise NotImplementedError

    def _append(self, items: Vault) -> Vault:
        """Return all duplicated"""
        raise NotImplementedError

    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:
    # NEXT:


class V2[Item, Vault: Vaults, U, A]:
    vault: Vault

    def _empty(self) -> Vault:
        raise NotImplementedError

    def _as_vault(self, items: Any, /) -> Vault:
        raise NotImplementedError

    def _merge(self, vault: Vault, incoming: Vault) -> Vault:
        raise NotImplementedError

    def _subtract(self, vault: Vault, targets: Vault) -> tuple[Vault, Vault]:
        raise NotImplementedError

    def _collisions(self, incoming: Vault) -> Vault:
        raise NotImplementedError

    def _at(self, uid: U) -> Item | None:
        raise NotImplementedError

    def _select(self, id: A) -> Vault:
        raise NotImplementedError

    def _slice(self, s: slice) -> Vault:
        raise ValueError(f"Slicing not supported: {s!r}", s)

    def vault(self) -> Iterator[Item]:
        yield from self.vault
