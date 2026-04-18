from functools import singledispatchmethod
from pathlib import Path


class FilterSet[SetType: str | Path | int, ObjectType]:
    def __init__(
        self,
        exclude: set[SetType] | None = None,
        require_all: set[SetType] | None = None,
        require_any: set[SetType] | None = None,
        get_complementary_negative_set: bool = False,
    ):
        self.require_all: set[SetType] = require_all or set()
        self.require_any: set[SetType] = require_any or set()
        self.exclude: set[SetType] = exclude or set()
        self.return_if_not_hit: bool = get_complementary_negative_set

    @singledispatchmethod
    def __call__(self, target):
        raise NotImplementedError(f"Cannot process {type(target)=}")

    @__call__.register
    def _(self, target: str | Path | int) -> bool:
        """String input -> returns filename string"""
        target_set: set[SetType] = self._create_target_set(target)
        return self._target_set_fullfils_conditions(target_set)

    @__call__.register
    def _(self, target: list) -> list[ObjectType]:
        """String input -> returns filename string"""
        filtered: list[ObjectType] = []

        for item in target:
            target_set: set[SetType] = self._create_target_set(item)
            hit: bool = self._target_set_fullfils_conditions(target_set)

            # Attach hit or not hit depending if flag is active
            if hit != self.return_if_not_hit:
                filtered.append(item)

        return filtered

    @singledispatchmethod
    def _create_target_set(self, target: ObjectType) -> set[SetType]:
        raise NotImplementedError(f"Cannot process {type(target)=}")

    @_create_target_set.register
    def _(self, target: str | Path | int) -> set:
        return {target}

    def _target_set_fullfils_conditions(
        self, target_set: set[SetType]
    ) -> bool:
        """Compares set with target keywords with internal registry"""
        # from loguru import logger

        # Condition 1: Must NOT have any excluded keywords
        if self.exclude and not target_set.isdisjoint(self.exclude):
            # logger.debug(f"{target_set=}, {self.exclude=}")
            return False

        # Condition 2: Must have ALL required keywords
        if self.require_all and not self.require_all.issubset(target_set):
            # logger.debug(f"{target_set=}, {self.require_all=}")
            return False

        # Condition 3: Must have AT LEAST ONE required_any keyword
        if self.require_any and target_set.isdisjoint(self.require_any):
            # logger.debug(f"{target_set=}, {self.require_any=}")
            return False

        return True
