"""
FilterSet: Core Engine as Base for Specifications

- Prepare Cascade of Filters

                             DependencyLevel.sstcore.util.filter[1]
"""

__all__: list[str] = [
    "FilterSet",
]

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, overload

from ...port.filter import Filter
from ...port.link import portlink
from ._base import FilterData


@portlink(Filter)
@dataclass
class FilterSet[SetType: str | Path | int, TargetT: Any](FilterData[SetType]):
    """Wire different Checks and Execute when Called"""

    @overload
    def __call__(self, target: TargetT) -> bool: ...
    @overload
    def __call__(self, target: list[TargetT]) -> list[TargetT]: ...
    @overload
    def __call__(self, target: set[TargetT]) -> set[TargetT]: ...
    @overload  # TODO: Check Iterator/Iterable
    def __call__(self, target: Iterable[TargetT]) -> Iterable[TargetT]: ...

    def __call__(
        self, target: TargetT | Iterable[TargetT]
    ) -> bool | Iterable[TargetT]:
        """Dispatch to single item (bool) or list filtering"""
        match target:
            case list():
                return list(self._fulfill_filter(target))
            case set():
                return set(self._fulfill_filter(target))
            case Iterable():
                yield self._fulfill_filter(target)
            case _:
                return self._fulfill(target)

    def _fulfill(self, target: TargetT) -> bool:
        """Override for custom validation"""
        return self.fulfills_trio({target})

    def _fulfill_filter(self, target: Iterable[TargetT]) -> Iterable[TargetT]:
        # TODO: Check Iterator/Iterable
        """Provide 'hits' or 'missing' items depending on flag"""
        for item in target:
            if self._fulfill(item) != self.return_opposite:
                yield item

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
