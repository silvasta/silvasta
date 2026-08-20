"""
Prepare Cascade of Filters

- FilterSet: Implement Core Logic as Base for Specifications
                                                 DependencyLevel[1]
"""

__all__: list[str] = [
    "FilterSet",
]

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload

from ...port.filter import Filter
from ._base import FilterData


@dataclass
class FilterSet[SetType: str | Path | int, TargetT: Any](FilterData[SetType]):
    @overload
    def __call__(self, target: TargetT) -> bool: ...
    @overload
    def __call__(self, target: list[TargetT]) -> list[TargetT]: ...

    def __call__(
        self, target: TargetT | list[TargetT]
    ) -> bool | list[TargetT]:
        """Dispatch to single item (bool) or list filtering"""
        if isinstance(target, list):
            return self._fulfill_filter(target)
        return self._fulfill(target)

    def _fulfill(self, target: TargetT) -> bool:
        """Override for custom validation"""
        return self.fulfills_trio({target})

    def _fulfill_filter(self, target: list) -> list[TargetT]:
        """Provide 'hit' or 'missing' items depending on flag"""
        return [item for item in target if self(item) != self.return_opposite]

    def fulfills_exclude(self, target_set: set[SetType]) -> bool:
        if self.exclude:
            if not self.exclude.isdisjoint(target_set):
                return False
        return True

    def fulfills_require_all(self, target_set: set[SetType]) -> bool:
        if self.require_all:
            if not self.require_all.issubset(target_set):
                return False
        return True

    def fulfills_require_any(self, target_set: set[SetType]) -> bool:
        if self.require_any:
            if self.require_any.isdisjoint(target_set):
                return False
        return True

    def fulfills_trio(self, target_set: set[SetType]) -> bool:
        if not self.fulfills_exclude(target_set):
            return False
        if not self.fulfills_require_all(target_set):
            return False
        if not self.fulfills_require_any(target_set):
            return False
        return True


if TYPE_CHECKING:
    _is_instance: Filter = FilterSet()
    _is_class: type[Filter] = FilterSet
