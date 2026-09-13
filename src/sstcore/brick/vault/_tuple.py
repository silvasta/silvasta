"""
TupleRegistry - Main Variation of the Core Registry

-
"""

from pathlib import Path

__all__: list[str] = [
    "TupleRegistry",
]

from collections.abc import Iterable
from typing import TYPE_CHECKING, NoReturn, Self, overload

from ...port.register import TupleRegister


class TupleRegistry[ItemT]:
    """Implement the Shape of the Registry with Tuples"""

    def __init__(self, items: tuple[ItemT, ...], **_kwargs):
        for item in items:
            # IDEA: this for all sequence registry? or even all?
            self._guard_input(item)
        self.vault: tuple[ItemT, ...] = tuple(items)

    def _guard_input(self, item) -> None | NoReturn:
        # IDEA: this for all sequence registry? or even all?
        """LATER: define Error Handling, on which level?"""

    def add(self, items: tuple[tuple[ItemT, int]], **_kwargs) -> Self:
        """Extend Items directly or with processing"""
        modified_data: list[ItemT] = list(self.vault)
        for item, index in items:
            if index in self:
                # TASK: insertion order
                # - find system to solve this
                modified_data.insert(index, item)
        return type(self)(items=tuple(modified_data))

    def get(self, key: int) -> ItemT | None:
        if key in self:
            return self.vault[key]
        return None

    @overload
    def clear(self, key: None) -> tuple[ItemT, ...]: ...
    @overload
    def clear(self, key: int) -> ItemT: ...
    def clear(self, key: int | None = None) -> tuple[ItemT, ...] | ItemT:
        """Delete and return full registry or return selected element"""
        old_data: tuple[ItemT, ...] | ItemT = (
            self.vault[key]
            if key is not None and key in self
            else tuple(*self.vault)
        )
        self.vault = ()
        return old_data

    def __iter__(self) -> Iterable[ItemT]:
        return iter(self.vault)

    def __len__(self) -> int:
        return len(self.vault)

    def __contains__(self, target) -> bool:
        return (target is None) or (0 <= target < len(self))


if TYPE_CHECKING:
    _instance: TupleRegister[Path, int] = TupleRegistry[Path](tuple(Path()))
    _class: type[TupleRegister[Path, int]] = TupleRegistry[Path]
