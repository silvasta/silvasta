from dataclasses import dataclass, field
from functools import singledispatchmethod
from pathlib import Path

from ._debug import debug_log

# TASK: check SetType and ObjectType
# - int ever used or needed?
# - ObjectType ever different from SetType?
# - list[ObjectType]? maybe that as Type or dispatch


@dataclass
class FilterSet[SetType: str | Path | int, ObjectType]:
    """Take input and answer if it matches the loaded criteria!"""

    exclude: set[SetType] = field(default_factory=set)
    require_all: set[SetType] = field(default_factory=set)
    require_any: set[SetType] = field(default_factory=set)

    allow_hidden_files: bool = False

    # Get complementary negative set, all not matching criteria
    return_if_not_hit: bool = False

    _debug: bool = False

    @singledispatchmethod
    def __call__(self, target):
        raise NotImplementedError(f"Cannot process {type(target)=}")

    @__call__.register
    def _(self, target: str | Path | int) -> bool:
        # TASK: put ObjectType,SetType here
        """String input -> returns filename string"""
        target_set: set[SetType] = self._create_target_set(target)
        return self.fulfills_all_conditions(target_set)

    @__call__.register
    def _(self, target: list) -> list[ObjectType]:
        """String input -> returns filename string"""
        filtered: list[ObjectType] = []

        for item in target:
            # TASK: combine set, then filter over all?
            target_set: set[SetType] = self._create_target_set(item)
            hit: bool = self.fulfills_all_conditions(target_set)

            # Attach 'hit' or 'not hit = missing' depending on flag
            if hit != self.return_if_not_hit:
                filtered.append(item)

        return filtered

    @singledispatchmethod
    def _create_target_set(self, target: ObjectType) -> set[SetType]:
        """Override this for specific object handling!"""
        # TODO: combined set?
        raise NotImplementedError(f"Cannot process {type(target)=}")

    @_create_target_set.register
    def _(self, target: str | Path | int) -> set:
        return {target}

    @debug_log
    def fulfills_exclude(self, target_set: set[SetType]) -> bool:
        """Condition 1: Must NOT have any excluded keywords"""
        # TODO: subhook for derivatives
        if self.exclude:
            # Must NOT have any excluded keywords
            if not self.exclude.isdisjoint(target_set):
                return False

        return True

    @debug_log
    def fulfills_require_all(self, target_set: set[SetType]) -> bool:
        """Condition 2: Must have ALL required keywords"""
        # TODO: subhook for derivatives
        if self.require_all:
            # Must have ALL required keywords
            if not self.require_all.issubset(target_set):
                return False

        return True

    @debug_log
    def fulfills_require_any(self, target_set: set[SetType]) -> bool:
        """Condition 3: Must have AT LEAST ONE required_any keyword"""
        # TODO: subhook for derivatives
        if self.require_any:
            # Must have AT LEAST ONE required_any keyword
            if self.require_any.isdisjoint(target_set):
                return False

        return True

    # TASK: make this extendable, 1 execution for all derivatives
    # - any derivative can assemble its own
    def fulfills_all_conditions(self, target_set: set[SetType]) -> bool:
        """Compare internal registry with target keyword set"""

        # TODO: combine the 3 below as general subhook
        if not self.fulfills_exclude(target_set):
            return False

        if not self.fulfills_require_all(target_set):
            return False

        if not self.fulfills_require_any(target_set):
            return False

        return True
