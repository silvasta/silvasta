"""
Experiments with python.bisect

Idea: Simple setup that absorbs complexity ready for fast apply
- Maintain sorted list of (threshold, value) pairs
- Use bisect to find the matching bucket in O(log n)
- Control behavior with policies

Bisect semantics:
- Sorted list, ascending! left is low, right is high
- bisect_left: insertion point to the LEFT of equal elements
- bisect_right: insertion point to the RIGHT of equal elements

"""

__all__: list[str] = [
    "BisectDTO",
    "BisectMixin",
    "BisectField",
    "InsertField",
    "BoundaryField",
    "BisectVault",
]
from bisect import bisect_left, bisect_right, insort_left, insort_right
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, overload

from ...port.link import portlink
from ...port.register import (
    BisectDTO,
    BisectPolicyBase,
    BoundaryPolicy,
    InsertPolicy,
)
from ..field import PolicyField
from ._base import BaseVault


@portlink(BisectDTO)
@dataclass
class BisectDTO[ThreshT: float | int, ObjecT: Any]:
    """Store threshold for bisectional comparison and corresponing value"""

    threshold: ThreshT
    value: ObjecT

    @property
    def label(self) -> str:
        return "Define label here..."

    def key(self) -> ThreshT:
        """Forward function to bisect"""
        return self.threshold

    def __str__(self) -> str:  # MOVE: to base class
        return f"{self.threshold}: {self.label}"

    def __repr__(self) -> str:  # MOVE: to base class
        return f"{type(self).__name__}({self})"


if TYPE_CHECKING:
    _dto: BisectDTO = BisectDTO(25, Any)


# @portlink(Register)
# @portlink(BisectRegister)
class BisectMixin[ThreshT: int | float]:
    """Collect python.bisect and provide for registry or other purposes"""

    vault: list[BisectDTO]

    def item_index(self, item: BisectDTO) -> int:
        """Get Position where next Item will be placed"""
        return self.thresh_index(item.threshold)

    def thresh_index(self, thresh: ThreshT) -> int:
        # TODO: some flag for the +- 1
        return self.left_index(thresh)

    def left_right_slice(self, key: ThreshT) -> slice:
        # TODO: some flag for the +- 1
        return slice(self.left_index(key) + 1, self.right_index(key) + 1)

    def left_index(self, thresh: ThreshT) -> int:
        """Match Exclusive tier boundaries ( > )"""
        left: int = bisect_left(self.vault, thresh, key=BisectDTO.key)
        # TODO: some flag for the +- 1
        return left - 1

    def right_index(self, thresh: ThreshT) -> int:
        """Match Inclusive tier boundaries"""
        right: int = bisect_right(self.vault, thresh, key=BisectDTO.key)
        # TODO: some flag for the +- 1
        return right - 1

    def attach_left(self, item: BisectDTO):
        """Attach new item on position < existing threshold members"""
        # TODO: some flag for the +- 1
        insort_left(self.vault, item.threshold, key=BisectDTO.key)

    def attach_right(self, item: BisectDTO):
        """Attach new item on position > existing threshold members"""
        insort_right(self.vault, item.threshold, key=BisectDTO.key)


class BisectField[EnumT: BisectPolicyBase](PolicyField[EnumT]):
    def __init__(self, *args, **kwargs):  # TODO: prepare bisect base?
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:  # LATER:
        return type(self).__name__


class BoundaryField(BisectMixin, BisectField[BoundaryPolicy]):
    def match(
        self,
        # NEXT: this comes not from arg but from... enum? how?
        policy: BoundaryPolicy,
        unit: BisectVault,  # TODO: attach self.vault somewhen?
        item: BisectDTO,
    ) -> int:

        match policy:
            case BoundaryPolicy.EXCLUSIVE:
                return self.left_index(item.threshold)

            case BoundaryPolicy.INCLUSIVE:
                return self.right_index(item.threshold)
        raise


class InsertField(BisectMixin, BisectField[BoundaryPolicy]):
    def match(
        self,
        # NEXT: this comes not from arg but from... enum? how?
        policy: InsertPolicy,
        unit: BisectVault,  # TODO: attach self.vault somewhen?
        item: BisectDTO,
    ):
        """Attach new item, Decide on Tie by interal policy or Raise"""

        match policy:
            case InsertPolicy.RAISE:
                if item in unit:
                    message = f"Thresh[{item.threshold}] already exists!"
                    raise ValueError(message, policy, unit, item)
                self.attach_right(item)

            case InsertPolicy.ALLOW_LEFT:  # LATER: add transition control
                self.attach_left(item)

            case InsertPolicy.ALLOW_RIGHT:  # LATER: add transition control
                self.attach_right(item)

            case InsertPolicy.OVERRIDE:
                if item in unit:
                    idx: int = self.item_index(item)
                    old_item: BisectDTO = self.vault[idx]
                    print(f"Override: {old_item=} -> new_{item=}")
                    self.vault[idx] = item
                else:
                    self.attach_right(item)


# @portlink(Vault)
# @portlink(BisectRegister)
class BisectVault[KeyT: float | int](BisectMixin, BaseVault[BisectDTO, list]):
    insert_mode = InsertField(InsertPolicy)
    boundry_mode = BoundaryField(BoundaryPolicy)

    def __init__(
        self,
        *items: BisectDTO,
        insert_policy: InsertPolicy = InsertPolicy.RAISE,
        boundary_policy: BoundaryPolicy = BoundaryPolicy.INCLUSIVE,
        dto_cls: type[BisectDTO] | None = None,  # TODO: check
    ) -> None:
        self.vault: list[BisectDTO] = []
        self.dto: type[BisectDTO] = dto_cls or BisectDTO

        self._insert_policy: InsertPolicy = insert_policy
        self._boundary_policy: BoundaryPolicy = boundary_policy

        self.add(*items)

    # def insert(self, item):  # IMPORTANT:
    #     type(self).insert_mode.execute(self, item)
    #
    # def compare(self, item):  # IMPORTANT:
    #     type(self).boundry_mode.execute(self, item)

    def __contains__(self, target: BisectDTO) -> bool:
        """Check if threshold exists in exactly one O(log(N)) pass"""
        idx: int = self.get(key=(thresh := target.threshold))
        return idx != len(self.vault) and self.vault[idx].threshold == thresh

    def get(self, key: KeyT) -> int:
        return self.thresh_index(thresh=key)

    # def add(
    #     self, *items: BisectDTO, override: bool = False
    # ) -> list[BisectDTO]:  # IDEA: override==True -> InsertPolicy.OVERWRITE?
    #     """
    #     You can Add with this but that results in high overhead!
    #
    #     - Recommended only when sorting is more important than speed,
    #       or at the very beginning when before starting with heavy usage
    #     """
    #     cleared: list[BisectDTO] = []
    #     for item in items:
    #         key: KeyT = self._item_identifier(item)  # TODO: item.threshold?
    #         if override:  # LATER: change override mode?
    #             cleared.extend(self.clear(key))
    #         # TODO: move insort to BisectMixin
    #         insort(self.vault, item, key=self._item_identifier)
    #     return cleared
    #
    # def find(self, key: KeyT) -> list[BisectDTO]:  # INFO: amazing
    #     """O(log n) lookup finding all items matching the key."""
    #     return self[self.left_right_slice(key)]
    #
    # def count(self, key: KeyT) -> int:  # INFO: amazing
    #     """O(log n) count without extracting the items."""
    #     return -self.left_index(key) + self.right_index(key)

    def _item_identifier(self, item: BisectDTO) -> KeyT:
        return item.key()

    def __repr__(self) -> str:  # LATER: format with indent etc.
        data: str = "\n".join(f"({d})" for d in self.vault)
        return f"{self}[\n{data}\n]" if data else f"{self}[...]"

    @overload
    def __call__(self, thresh: int, strict: Literal[True] = True) -> str: ...
    @overload
    def __call__(
        self, thresh: int, strict: Literal[False] = False
    ) -> str | None: ...

    def __call__(self, thresh: KeyT):
        """Provide the value corresponing to the matching threshold"""

        if not self.vault:
            message = f"{self} has no member, fill before access!"
            raise ValueError(message, thresh, self)

        if (index := self.get(thresh)) < 0:
            message = f"Incoming Thresh[{thresh}] below Min[{self.vault[0]}]!"
            raise ValueError(message, thresh, self)

        return self.vault[index].value


# class _BisectVault[ItemT, KeyT: Any]:
#     """
#     Idea 1 - Main Focus
#
#     - Read-optimized sorted Vault for O(log n) lookups
#
#     """
#
#     vault: list[ItemT]
#
#     # FIX: parametrize and match, allow for any base, but provide one
#     dto: type = BisectDTO
#
#     def __init__(
#         self,
#         # NEXT: check with potential common base:
#         # - probably at least BaseVault
#         # - unlikely direct from ListVault
#         # - maybe new SequenceVault(BaseVault)
#         #   -> shared base of TupleVault,ListVault,BisectVault
#         *items: ItemT,
#         insert_policy: InsertPolicy = InsertPolicy.RAISE,
#         boundary_policy: BoundaryPolicy = BoundaryPolicy.INCLUSIVE,
#     ) -> None:
#         self._insert_policy: InsertPolicy = insert_policy
#         # TASK: descriptor:
#         # - lock _insert_policy! no modification after init
#         # - _boundary_policy changeable , maybe temporary in with block
#         self._boundary_policy: BoundaryPolicy = boundary_policy
#         # FIX: key fails for method, needs staticmethod, like BisectDTO.key
#         # -> make this like function of BisectVault.dto
#         # -> provide _item_identifier from there and the staticmethod
#         self.vault = sorted(*items, key=self._item_identifier)
#
#     def with_dto(self, dto_type: type[ItemT]) -> Self:
#         # IDEA: something like this? or better in __init__ or cls-constructor?
#         """Update internal DTO class (recommended/possible once at the beginning)"""
#         self.dto: type[ItemT] = dto_type
#         return self  # TODO: maybe rebuild
#
#     def with_attach(self, threshs: list[KeyT], values: list[ItemT]) -> Self:
#         # TODO: check with BisectExecutor
#         """Provide Executor with updated internal data"""
#         for thresh, value in zip(threshs, values, strict=True):
#             self.add(thresh, value)
#         return self  # TODO: maybe rebuild
#
#     def add(
#         # TASK: check how much similarity to other SequenceVault makes sense
#         self,
#         *items: ItemT,  # NOTE: with the dtos it would work
#         override: bool = False,  # IDEA: True -> InsertPolicy.OVERWRITE, False: InsertPolicy.RAISE, and delete ALLOW_RIGHT/LEFT
#     ) -> list[ItemT]:
#         """
#         You can Add with this but that results in high overhead!
#
#         - Recommended only when sorting is more important than speed,
#           or at the very beginning when before starting with heavy usage
#         """
#         cleared: list[ItemT] = []
#         for item in items:
#             key = self._item_identifier(item)
#             if override:  # LATER: use override from BisectExecutor
#                 cleared.extend(self.clear(key))
#             # O(n) insertion because lists must shift elements
#             insort(self.vault, item, key=self._item_identifier)
#         # IDEA: just rebuild? probably faster for more items
#         return cleared
#
#     def find(self, key: KeyT) -> list[ItemT]:  # INFO: amazing
#         """O(log n) lookup finding all items matching the key."""
#         left = bisect_left(self.vault, key, key=self._item_identifier)
#         # AI_QUESTION: the type checker don't complains here, is the method possible?
#         right = bisect_right(self.vault, key, key=self._item_identifier)
#         return self.vault[left:right]
#
#     def count(self, key: KeyT) -> int:  # INFO: amazing
#         """O(log n) count without extracting the items."""
#         left = bisect_left(self.vault, key, key=self.dto.key)
#         # AI_QUESTION: otherwise, might just the dto.key be the most simple approach?
#         right = bisect_right(self.vault, key, key=self.dto.key)
#         return right - left
#
#     def _item_identifier(self, item: ItemT) -> KeyT:
#         return self.dto.key(item)
#
#
# class _SmartListVault[ItemT](ListVault[ItemT]):
#     # LATER:
#     # REFACTOR: extract useful parts or ideas
#     """
#     Idea for Extension
#
#     - Support ListVault on high troughput
#
#     Could maybe make sense, still low priority now.
#     """
#
#     BISECT_THRESHOLD = 50
#     _is_sorted: bool = False
#     #
#     # def add(self, *items: ItemT, override: bool = False) -> list[ItemT]:
#     #     self._is_sorted = False  # Mark dirty
#     #     return super().add(*items, override=override)
#     #
#     # def find(self, key: KeyT) -> list[ItemT]:
#     #     """Decide strategy based on threshold"""
#     #
#     #     if len(self.vault) >= self.BISECT_THRESHOLD:
#     #         if not self._is_sorted:
#     #             self.vault.sort(key=self._item_identifier)
#     #             self._is_sorted = True
#     #
#     #         left = bisect_left(self.vault, key, key=self._item_identifier)
#     #         right = bisect_right(self.vault, key, key=self._item_identifier)
#     #         return self.vault[left:right]
#     #
#     #     # Fallback to linear
#     #     return super().find(key)
