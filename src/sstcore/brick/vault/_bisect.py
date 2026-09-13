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
    "BisectRegistry",
]
from bisect import bisect_left, bisect_right, insort, insort_left, insort_right
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, overload

from ...port.register import (
    BisectData,
    BisectPolicyBase,
    BoundaryPolicy,
    InsertPolicy,
)
from ..field._base import PolicyField
from ..vault._base import BaseRegistry


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
    _dto: BisectData = BisectDTO(25, Any)


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

    def attach_left(self, item: BisectData):
        """Attach new item on position < existing threshold members"""
        # TODO: some flag for the +- 1
        insort_left(self.vault, item.threshold, key=BisectData.key)

    def attach_right(self, item: BisectData):
        """Attach new item on position > existing threshold members"""
        insort_right(self.vault, item.threshold, key=BisectData.key)


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
        unit: BisectRegistry,  # TODO: attach self.vault somewhen?
        item: BisectDTO,
    ) -> int:

        match policy:
            case BoundaryPolicy.EXCLUSIVE:
                return self.left_index(item.threshold)

            case BoundaryPolicy.INCLUSIVE:
                return self.right_index(item.threshold)


class InsertField(BisectMixin, BisectField[BoundaryPolicy]):
    def match(
        self,
        # NEXT: this comes not from arg but from... enum? how?
        policy: InsertPolicy,
        unit: BisectRegistry,  # TODO: attach self.vault somewhen?
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


class BisectRegistry[KeyT: float | int](
    BisectMixin, BaseRegistry[list, BisectDTO, KeyT]
):
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

    def insert(self, item):  # IMPORTANT:
        type(self).insert_mode.execute(self, item)

    def compare(self, item):  # IMPORTANT:
        type(self).boundry_mode.execute(self, item)

    def __contains__(self, target: BisectDTO) -> bool:
        """Check if threshold exists in exactly one O(log(N)) pass"""
        idx: int = self.get(key=(thresh := target.threshold))
        return idx != len(self.vault) and self.vault[idx].threshold == thresh

    def get(self, key: KeyT) -> int:
        return self.thresh_index(thresh=key)

    def add(
        self, *items: BisectDTO, override: bool = False
    ) -> list[BisectDTO]:  # IDEA: override==True -> InsertPolicy.OVERWRITE?
        """
        You can Add with this but that results in high overhead!

        - Recommended only when sorting is more important than speed,
          or at the very beginning when before starting with heavy usage
        """
        cleared: list[BisectDTO] = []
        for item in items:
            key: KeyT = self._item_identifier(item)  # TODO: item.threshold?
            if override:  # LATER: change override mode?
                cleared.extend(self.clear(key))
            # TODO: move insort to BisectMixin
            insort(self.vault, item, key=self._item_identifier)
        return cleared

    def find(self, key: KeyT) -> list[BisectDTO]:  # INFO: amazing
        """O(log n) lookup finding all items matching the key."""
        return self[self.left_right_slice(key)]

    def count(self, key: KeyT) -> int:  # INFO: amazing
        """O(log n) count without extracting the items."""
        return -self.left_index(key) + self.right_index(key)

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
