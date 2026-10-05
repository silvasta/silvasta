from bisect import bisect_left, bisect_right, insort
from typing import Any, Self

from ..___bisect import BisectData, BisectHolding, BoundaryPolicy, InsertPolicy
from ._list import ListRegistry


class BisectRegistry[ItemT: BisectHolding, KeyT: Any]:
    """
    Idea 1 - Main Focus

    - Read-optimized sorted Registry for O(log n) lookups

    """

    vault: list[ItemT]

    # FIX: parametrize and match, allow for any base, but provide one
    dto: type[BisectHolding[KeyT, ItemT]] = BisectData

    def __init__(
        self,
        # NEXT: check with potential common base:
        # - probably at least BaseRegistry
        # - unlikely direct from ListRegistry
        # - maybe new SequenceRegistry(BaseRegistry)
        #   -> shared base of TupleRegistry,ListRegistry,BisectRegistry
        *items: ItemT,
        insert_policy: InsertPolicy = InsertPolicy.RAISE,
        boundary_policy: BoundaryPolicy = BoundaryPolicy.INCLUSIVE,
    ) -> None:
        self._insert_policy: InsertPolicy = insert_policy
        # TASK: descriptor:
        # - lock _insert_policy! no modification after init
        # - _boundary_policy changeable , maybe temporary in with block
        self._boundary_policy: BoundaryPolicy = boundary_policy
        # FIX: key fails for method, needs staticmethod, like BisectData.key
        # -> make this like function of BisectRegistry.dto
        # -> provide _item_identifier from there and the staticmethod
        self.vault = sorted(*items, key=self._item_identifier)

    def with_dto(self, dto_type: type[ItemT]) -> Self:
        # IDEA: something like this? or better in __init__ or cls-constructor?
        """Update internal DTO class (recommended/possible once at the beginning)"""
        self.dto: type[ItemT] = dto_type
        return self  # TODO: maybe rebuild

    def with_attach(self, threshs: list[KeyT], values: list[ItemT]) -> Self:
        # TODO: check with BisectExecutor
        """Provide Executor with updated internal data"""
        for thresh, value in zip(threshs, values, strict=True):
            self.add(thresh, value)
        return self  # TODO: maybe rebuild

    def add(
        # TASK: check how much similarity to other SequenceRegistry makes sense
        self,
        *items: ItemT,  # NOTE: with the dtos it would work
        override: bool = False,  # IDEA: True -> InsertPolicy.OVERWRITE, False: InsertPolicy.RAISE, and delete ALLOW_RIGHT/LEFT
    ) -> list[ItemT]:
        """
        You can Add with this but that results in high overhead!

        - Recommended only when sorting is more important than speed,
          or at the very beginning when before starting with heavy usage
        """
        cleared: list[ItemT] = []
        for item in items:
            key = self._item_identifier(item)
            if override:  # LATER: use override from BisectExecutor
                cleared.extend(self.clear(key))
            # O(n) insertion because lists must shift elements
            insort(self.vault, item, key=self._item_identifier)
        # IDEA: just rebuild? probably faster for more items
        return cleared

    def find(self, key: KeyT) -> list[ItemT]:  # INFO: amazing
        """O(log n) lookup finding all items matching the key."""
        left = bisect_left(self.vault, key, key=self._item_identifier)
        # AI_QUESTION: the type checker don't complains here, is the method possible?
        right = bisect_right(self.vault, key, key=self._item_identifier)
        return self.vault[left:right]

    def count(self, key: KeyT) -> int:  # INFO: amazing
        """O(log n) count without extracting the items."""
        left = bisect_left(self.vault, key, key=self.dto.key)
        # AI_QUESTION: otherwise, might just the dto.key be the most simple approach?
        right = bisect_right(self.vault, key, key=self.dto.key)
        return right - left

    def _item_identifier(self, item: ItemT) -> KeyT:
        return self.dto.key(item)


class _SmartListRegistry[ItemT, KeyT](ListRegistry[ItemT, KeyT]):
    # LATER:
    # REFACTOR: extract useful parts or ideas
    """
    Idea for Extension

    - Support ListRegistry on high troughput

    Could maybe make sense, still low priority now.
    """

    BISECT_THRESHOLD = 50
    _is_sorted: bool = False

    def add(self, *items: ItemT, override: bool = False) -> list[ItemT]:
        self._is_sorted = False  # Mark dirty
        return super().add(*items, override=override)

    def find(self, key: KeyT) -> list[ItemT]:
        """Decide strategy based on threshold"""

        if len(self.vault) >= self.BISECT_THRESHOLD:
            if not self._is_sorted:
                self.vault.sort(key=self._item_identifier)
                self._is_sorted = True

            left = bisect_left(self.vault, key, key=self._item_identifier)
            right = bisect_right(self.vault, key, key=self._item_identifier)
            return self.vault[left:right]

        # Fallback to linear
        return super().find(key)
