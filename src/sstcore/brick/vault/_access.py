"""
The Operators to Set and Get items from the Vault

-
"""

__all__: list[str] = [
    "VaultAccess",
    "VaultReader",
    "VaultWriter",
]

from typing import Any, overload

from ...port.register import registry_types as _r
from ._contract import VaultContract


class VaultReader[Item, V: _r.Vault](VaultContract[Item, V]):
    """Pick the Items from the Vault"""

    @overload
    def __getitem__(self, query: int) -> Item: ...
    @overload
    def __getitem__(
        self, query: slice | _r.Predicate | tuple[Any, ...]
    ) -> V: ...
    @overload
    def __getitem__(self, query: str) -> Item: ...

    def __getitem__(self, query: _r.Selector[Item]) -> Item | V:
        return self._dispatch_get(query)

    def _dispatch_get(self, query: Any) -> Item | V:
        match query:
            case int() as idx if not isinstance(idx, bool):
                return self._index_item(idx)

            case slice() as sl:
                return self._slice(sl)

            case str() as key:
                return self._key_item(key)

            case tuple() as keys:
                return self._gather(keys)

            case fn if callable(fn):
                return self._where(fn)
            case _:
                raise TypeError(f"Unsupported: {type(query).__name__}")


class VaultWriter[Item, V: _r.Vault](VaultContract[Item, V]):
    """Place the Items in the Vault"""

    def __setitem__(self, query: _r.Selector[Item], value: Any) -> None:
        self._dispatch_set(query, value)

    def _dispatch_set(self, query: Any, value: Any) -> None:
        match query:
            case int() as idx if not isinstance(idx, bool):
                self._index_put(idx, self._normalize(value))

            case slice() as sl:
                self._slice_put(sl, value)

            case str() as key:
                self._key_put(key, self._normalize(value))

            case tuple() as keys:
                self._scatter(keys, value)

            case fn if callable(fn):
                self._replace_where(fn, self._normalize(value))
            case _:
                raise TypeError(f"Unsupported: {type(query).__name__}")

    def _scatter(self, keys: tuple[Any, ...], value: Any) -> None:
        values: list[Any] = list(value)
        if len(keys) != len(values):
            raise ValueError(
                f"Cannot unpack {len(values)} values into {len(keys)} selectors"
            )
        for key, item in zip(keys, values, strict=True):
            self[key] = item


class VaultAccess[Item, V: _r.Vault](
    VaultWriter[Item, V], VaultReader[Item, V]
): ...
