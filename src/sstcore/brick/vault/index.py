"""
IndexRegistry - Specialized Main Variation of the Core Registry

- Tuples controlled by multiple Enum Axes indexed from 0
  (unsure if that will ever be completed or useful)

"""

__all__: list[str] = [
    # "IndexRegistry",
]

from enum import auto
from typing import Any, Literal

from ...port.register import Index


class GridIndex(Index):
    ALPHA = auto()
    BETA = auto()
    DELTA = auto()


index_is_zero: int = GridIndex.ALPHA.value
parse_by_name: Literal["ALPHA", "BETA", "DELTA"] = GridIndex["BETA"].name

automate_this_if_ever_used: tuple[Any, ...] = tuple(
    f"data of {index}" for index in GridIndex
)

for index in GridIndex:  # NOTE: the entire idea based on this
    print(automate_this_if_ever_used[index.value])


class _TupleIndexRegistry[ItemT, IndexT]:
    ...
    # FIX: with next try Enum Meta Hack
    # IDEA: multi dimensional grid
    # - auto-generated enums with index for grid
    # - at runtime use enum coordinates for access
    # - most likely tuple based, try to keep flexible
    # - static: define protocol around enum
    # def __init__(self, index: type[IndexT], items: tuple[ItemT, ...]) -> None:
    #     if len(items) != len(index):
    #         raise ValueError(f"need {len(index)} items, got {len(items)}")
    #     self.index = index
    #     self.items = items
    #     self._by_name = {m.name.lower(): m for m in index}
    #
    # def __len__(self) -> int:
    #     return len(self.items)
    #
    # def __contains__(self, target: Any) -> bool:
    #     try:
    #         self.resolve(target)
    #         return True
    #     except KeyError, ValueError:
    #         return False
    #
    # @property
    # def all(self) -> Iterable[ItemT]:
    #     return self.items
    #
    # def resolve(self, key: Index | int | str) -> Index:
    #     if isinstance(key, self.index):
    #         return key
    #     if isinstance(key, int):
    #         return self.index(key)  # ty.ignore
    #     return self._by_name[str(key).lower()]
    #
    # def get(self, key: Index | int | str) -> ItemT:
    #     return self.items[self.resolve(key).value]
