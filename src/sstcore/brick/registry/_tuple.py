"""
TupleRegistry - Main Variation of the Core Registry

-
"""

__all__: list[str] = [
    "TupleRegistry",
]

from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any

from ...port.register import TupleRegister


# NEXT: Tuple Registry
# - add = rebuild or error if locked
# - encode rules, similar like above
# - visualize with index
# - sort! rebuild and apply new sorting
# - no mixing here!
# -> only gatekeeper for new mixins and order
class TupleRegistry[ItemT]:  # TODO: derive??
    """An immutable, high-speed contiguous array-backed registry."""

    __slots__ = ("_items", "_identifiers")

    def __init__(self, items: Iterable[ItemT], key_fn: Callable[[ItemT], Any]):
        self._items: tuple[ItemT, ...] = tuple(items)
        self._identifiers: tuple[Any, ...] = tuple(
            key_fn(item) for item in self._items
        )

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, key: Any) -> bool:
        return key in self._identifiers

    def __iter__(self) -> Iterator[ItemT]:
        return iter(self._items)

    @property
    def all(self) -> tuple[ItemT, ...]:
        return self._items

    def get(self, key: Any) -> ItemT | None:
        try:
            idx = self._identifiers.index(key)
            return self._items[idx]
        except ValueError:
            return None


if TYPE_CHECKING:
    _instance: TupleRegister = TupleRegistry()
    _class: type[TupleRegister] = TupleRegistry
