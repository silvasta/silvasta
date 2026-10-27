"""
Prepare Cascade of Filters

- FilterData: Set Container with Arguments and Modification
  (No Filtering here)

                             DependencyLevel.sstcore.util.filter[0]
"""

__all__: list[str] = [
    "FilterData",
]

from collections.abc import Set
from dataclasses import dataclass, field
from typing import Self

from ...port.filter import FilterSpec
from ...port.link import portlink


@portlink(FilterSpec)
@dataclass
class FilterData[SetType]:
    exclude: set[SetType] = field(default_factory=set)
    require_all: set[SetType] = field(default_factory=set)
    require_any: set[SetType] = field(default_factory=set)

    allow_hidden_files: bool = False
    return_opposite: bool = False

    @classmethod
    def clone(cls, args: FilterSpec[SetType]) -> Self:
        return cls(
            exclude=set(args.exclude),
            require_all=set(args.require_all),
            require_any=set(args.require_any),
            allow_hidden_files=args.allow_hidden_files,
            return_opposite=args.return_opposite,
        )

    @classmethod
    def defrost(
        cls,
        exclude: Set[SetType] | None = None,
        require_all: Set[SetType] | None = None,
        require_any: Set[SetType] | None = None,
        *,
        allow_hidden_files: bool = False,
        return_opposite: bool = False,
    ) -> Self:
        """Create Filter from (Frozen-)Set"""
        return cls(
            exclude=set(exclude) if exclude is not None else set(),
            require_all=set(require_all) if require_all is not None else set(),
            require_any=set(require_any) if require_any is not None else set(),
            allow_hidden_files=allow_hidden_files,
            return_opposite=return_opposite,
        )

    def merge(self, args: Self) -> Self:
        self.exclude.update(args.exclude)
        self.require_all.update(args.require_all)
        self.require_any.update(args.require_any)
        return self

    def subtract(self, args: Self) -> Self:
        self.exclude.difference_update(args.exclude)
        self.require_all.difference_update(args.require_all)
        self.require_any.difference_update(args.require_any)
        return self
