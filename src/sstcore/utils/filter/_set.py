"""
Prepare Cascade of Filters

- FilterSet as Base for different purposes

                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "FilterSet",
    "FilterArgs",
]

from dataclasses import dataclass
from functools import singledispatchmethod
from pathlib import Path
from typing import Any

from ...error import NotImplementedDispatchError
from ...port.filter import FilterArgs


@dataclass
class FilterSet[SetType: str | Path | int, TargetT: Any](FilterArgs[SetType]):
    """Take input and answer if it matches the loaded criteria!"""

    @singledispatchmethod
    def __call__(self, target):
        """Dispatch to Single execution or List handling"""
        raise NotImplementedDispatchError(target)

    @__call__.register
    def _(self, target: str | Path | int) -> bool:
        """Check if target fulfills set conditions and validation"""
        target_set: set[SetType] = self._create_target_set(target)
        return self._fulfills_conditions(target, target_set)

    @__call__.register
    def _(self, target: list) -> list[TargetT]:
        """Provide 'hit' or 'missing' Objects depending on flag"""
        return [item for item in target if self(item) != self.return_opposite]

    def _fulfills_conditions(self, target: TargetT, target_set: set) -> bool:
        """Override for custom validation"""
        return self.fulfills_condition_trio(target_set)

    def _create_target_set(self, target: TargetT) -> set[SetType]:
        """Override this for specific object handling!"""
        return {target}

    def fulfills_exclude(self, target_set: set[SetType]) -> bool:
        """Condition 1: Must NOT have any excluded keywords"""

        if self.exclude:
            if not self.exclude.isdisjoint(target_set):
                return False

        return True

    def fulfills_require_all(self, target_set: set[SetType]) -> bool:
        """Condition 2: Must have ALL required keywords"""

        if self.require_all:
            if not self.require_all.issubset(target_set):
                return False

        return True

    def fulfills_require_any(self, target_set: set[SetType]) -> bool:
        """Condition 3: Must have AT LEAST ONE required_any keyword"""

        if self.require_any:
            if self.require_any.isdisjoint(target_set):
                return False

        return True

    def fulfills_condition_trio(self, target_set: set[SetType]) -> bool:
        """Check if all 3 conditions are fulfilled"""

        if not self.fulfills_exclude(target_set):
            return False
        if not self.fulfills_require_all(target_set):
            return False
        if not self.fulfills_require_any(target_set):
            return False

        return True
